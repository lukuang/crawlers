use strict;
use lib 'extra_mods';
use lib 'extra_mods/5.8';
use JSON;
use LWP::Protocol::https;
use Net::OAuth;
use LWP::UserAgent;
use Data::Dumper;
use LWP::Simple;
use Mozilla::CA;
use HTTP::Request;
use HTTP::Response;
use POSIX qw(strftime);

my $previous_time = strftime"%F-%H", gmtime;
print "Start at ".$previous_time."\n";
my $browser = LWP::UserAgent->new('IE 6');
$browser->timeout(10);


$Net::OAuth::PROTOCOL_VERSION = Net::OAuth::PROTOCOL_VERSION_1_0;

my $expected_result_format = 'json'; #xml or json

my %urls;
my %args;
my @all_results;
$args{q} = "((Nepal)or(earthquake))"; # This is the query we are searching for
$args{format} = $expected_result_format;
$args{count} = 50; # number of results to be returned
$args{start} = 0;
my $start;
my $count;
my $total_count;
my $array_ref;
my $temp;
my $buckets = "news"; # news,web,images (various BOSS services)
while(1){
    $args{count} = 50; # number of results to be returned
    $args{start} = 0;
    $temp = get_response(\%args,$buckets);
    #print $temp;
    #die;
    ($start,$count, $total_count,$array_ref) = store_result($temp);
    printf "get %d results\n", scalar(@{$array_ref});
    push(@all_results,@{$array_ref});
    while($start+$count<$total_count && $start+$count<=1000){
        $args{start} = $start + $count;
        if ($start + $count > $total_count){
            $args{count} = $total_count - $start
        }
        $temp = get_response(\%args,$buckets);
        ($start,$count, $total_count,$array_ref) = store_result($temp);
        printf "get %d results\n", scalar(@{$array_ref});
        push(@all_results,@{$array_ref});
    }
    save_urls();

    
    my $re = encode_json \@all_results;
    my $current_time = strftime"%F-%H", gmtime;
    print "finished crawl at time $current_time\n";
    printf "result size is %d\n", scalar(@all_results);
    my $out = "data/".$current_time;
    open(OUT,">$out") or die "cannot open $out\n$!\n";
    print OUT $re;
    @all_results = ();
    sleep(3600);
    
}
#print $temp;

sub store_result{
    my $temp = shift;
    my $response = decode_json $temp;
    #print $response;
    my @result_array;
    if (exists $response->{"bossresponse"}){
    	
    	if($response->{"bossresponse"}->{"responsecode"}==200){
    		print "correct code\n";
            my $sub_response = $response->{"bossresponse"}->{"news"};
    		my $start = $response->{"bossresponse"}->{"news"}->{"start"},"\n";
    		my $count = $sub_response->{"count"},"\n";
    		my $total_count = $sub_response->{"totalresults"},"\n";
            print "start: $start\tcount: $count\ttotal: $total_count\n";
            #return($start,$count, $total_count, \@result_array);
            my $dup_count = 0;
    		foreach my $item(@{$sub_response->{"results"}} ){
    			if (not exists $urls{$item->{"url"}}){
    				
    				my $request = HTTP::Request->new(GET => $item->{"url"});
                    my $url_response = $browser->request($request);
    			    if($url_response->is_error()){
                        #print "cannot get url content\n";
                        next;
                    }
                    else{
                        #print "new url",$item->{"url"},"\n";
                        $urls{$item->{"url"}} = 1;
                        my $url_content = $url_response->content;
                        $item->{"content"} = $url_content;
                        push(@result_array,$item);
    			     }
                }
                else{
                    $dup_count++;
                }
    		}
            print "there are $dup_count duplicate results\n";
            
            #print $re;
    		#"start":"50","count":"50","totalresults":"289"
            return($start,$count, $total_count, \@result_array);
    	}
    	else{
            
            print "response code error\n";
            print $response->{"bossresponse"}->{"responsecode"};
            save_urls();
            die;
    	}
    }
    else{
        print "wrong result syntax\n";
        print temp;
        save_urls();
        die;
    }

}
#print $response->{"bossresponse"};

sub get_response {
    my %args = %{(shift)};
    my $buckets = shift;

    my $ua = LWP::UserAgent->new(ssl_opts=>{ verify_hostname => 0, SSL_ca_file => Mozilla::CA::SSL_ca_file()});


    my $auth = $ARGV[0];

    open(OUT,"$auth") or die "cannot open $auth\n$!\n";
    my $cc_key = <OUT>;
    chomp $cc_key;
    #print $cc_key."\n";
    my $cc_secret = <OUT>;
    chomp $cc_secret;
    #print $cc_secret."\n";
    my $oauth_token=<OUT>;
    chomp $oauth_token;
    #print $oauth_token."\n";
    my $oauth_token_secret=<OUT>;
    chomp $oauth_token_secret;
    #print $oauth_token_secret."\n";

    close(OUT);


    # Source Url
    my $url = "https://yboss.yahooapis.com/ysearch/$buckets";

    # Create request
    my $request = Net::OAuth->request("request token")->new(
            consumer_key => $cc_key,
            consumer_secret => $cc_secret,
            #oauth_token => $oauth_token,
	    #oauth_token_secret => $oauth_token_secret,
            request_url => $url,
            request_method => 'GET',
            signature_method => 'HMAC-SHA1',
            timestamp => time,
            nonce => 'kuangNepalCrawl'+time,
            callback => "oob",
            extra_params => \%args
            );

    # Sign request
    $request->sign;

    # Get message to the Service Provider
    my $res = $ua->get($request->to_url);

    # If request is success, display content
        if ($res->is_success) {
            return $res->content;
        }
        else {
        # Print error and die
            #print "something";
            print $res;
            Dumper $res;
            print "Something went wrong\n";
            save_urls();
            die;
            #die "Something went wrong";
        }
}

sub save_urls{
    my $time_now = strftime"%F-%H", gmtime;
    my $out = "urls";
    print "store urls already retrieved at $time_now\n";
    open(OUT,">$out") or die "cannot open $out\n$!\n";
    my $retrieved_urls = encode_json \%urls;
    print OUT $retrieved_urls; 
    
}

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

    # PROVIDE YOUR KEY HERE
    my $cc_key = "dj0yJmk9cEp3clF5cld6WE5VJmQ9WVdrOWIxbHRkMnBxTmpRbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1iMg--";

    # PROVIDE YOUR SECRET HERE
    my $cc_secret = "8fd17d9d22e233c914f5beec766a46db8f4ee077";

    my $oauth_token="A%3Dr9Ww9p7tgQ_a5GInZBA_qWYc_.8wWiyk57tgTgirPLQUo_0fHZ5N9qChYGj4UCRFC.IbNA9RJ_1lAqUdZLDl3wnwBt_XbYb7dkXB0cl8.GUCXhDsvaDcO14n_4xI5VHp41u76bvo8R0tgTuccbiubPMUlm8Ok.DaJSv0cpuFuosag5oRnmRbDnfJlmbE1cqYR703n.GRXNN0OKFt.TbGRk9JQ5kEnHV.wSKoKK6oY59ROvkfJwm99lNghVnW6vbMi0rKCKdZCrKAp_DxE0BtiiwxYlp02tX3H.Jo4N7XBjsB_pypSFNoFzz_BHW7rznS_P3owFzCziVDm536oRag3m7Z_mZ.RzJBfz2WKqRQlI11RdZpM1LW1uePRftpNu_A9hWXrceWwqMHiEZgeXUkR1DrwrBX5BqQdO3QL2yyny7fvwV8rvNurz6TdxN_qz6QpfIrlXsT6YjR7ifQBkz3q95hRH6yOHi0anEpsdzjkfOsNDsyRAlMclEhkSlHe7S_HYiLZJ3vkegj3o8UNyoc69pl_eSkkL4.JX40weIckDqFUxvA0iuwJQc8ySN_nkp6qDsLlxMDXugAaUfWxKjRh_9Sj7_Bonm7o_3XL_gDm8pI9mbFVhLlwbvvRRlzzw6hj7Hnaf7fk3Vi2zh0vFGNSPM16CiyD6tC5ChajocNCVeWSxZwboCbQJr6vXXLMdgq.C6vfjZKsPyybd0HU39gJcUbaShsMKkaCer0fvlhDQNtU7VzvJzlfr38xNfFRvMd4netQpbcDt46VeLzwarjY7Tjv1hkEFxnKfd6MpzzUA--&";
    
	my $oauth_token_secret="8234e7b429d93ebbe5363357999628e20a5830d0";
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

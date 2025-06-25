<?php 
  require "google-api-php-client/vendor/autoload.php";
  
  $clientId="<CLIENT_ID>";
  $clientSecret="<CLIENT_SECRET>";
  $redirectURI="<REDIRECT_URI>";
  
  $client=new Google_Client();
  $client->setClientId($clientId);
  $client->setClientSecret($clientSecret);
  $client->setRedirectURI($redirectURI);
  $client->addScope("email");
  $client->addScope("profile");
?>
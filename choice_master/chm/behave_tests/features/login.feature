Feature: Login to the system
  As a user I want to be able to sign up using
  my account of github or gmail, or my existing
  account of Choice Master

  Scenario: Not logged in users are redirected to login page
    When I go to the "home" page
    Then I am redirected to the "login" page

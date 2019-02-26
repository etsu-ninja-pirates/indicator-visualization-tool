# Created by Jean-Marie at 2/21/2019
Feature: Open CPH IVT
  In order to visualize county ranking
  As a user of CPH-IVT
  I want to be able to get on the home page

  Scenario: Confirm that I am on the home page of the application
    Given I am on public user home page
    When I go to the "/" page
    Then I see content "Find a Location"
#### Guideline for approving a pull request
This file contains guidelines that should be followed when making changes the the repository.
When Reviewing code before merging a PR, ensure that the following steps are honored.
All developers tasked to review pull requests must ensure that the following list is met for a pull request to be marked as approved.

#### Every uploaded file should have a block comment at the top listing
- The main purpose of the file
- First Name of the author of the file
- All `methods` that are developed using external help should have a `link` showing where the developer got the idea for using a particular technique to solve a problem at hand.

#### Use Docstring to describe `Classes` and `Methods`
Format of choice `reStructuredText` (reST): See Example
`"""This is a reST style.`
`:param param1: this is a first param`
`:param param2: this is a second param`
`:returns: this is a description of what is returned`
`:raises keyError: raises an exception`
`"""`
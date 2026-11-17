# Approved test cases

## TC-01: Login succeeds with valid credentials
- **Type:** positive | **Priority:** high
- **Preconditions:** A registered, unlocked account exists.
- **Steps:**
  1. Open the login page
  2. Enter a valid email
  3. Enter the correct password
  4. Click Log in
- **Expected:** The user lands on their account page.

## TC-03: hello world
- **Type:** edge | **Priority:** high
- **Preconditions:** A registered account exists with no prior failed attempts.
- **Steps:**
  1. Attempt login with a wrong password 5 times
  2. Attempt login with the correct password
- **Expected:** The account is locked for 15 minutes and the correct password is rejected.

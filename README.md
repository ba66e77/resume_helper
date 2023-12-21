# Resume Helper

From a default resume in GDrive, make a copy of the file renamed to include a role modifier. For example, if applying to
"Role X" and "Company Y", it would create a copy of the template file with a new name of "Resume - Company X - Role Y".

Code _heavily_ based upon example code in https://developers.google.com/docs/api/quickstart/python.

## Set up and use

1. Follow the instructions for setting up an application and downloading a credentials.json in the developers.googlee link above.
1. Edit the constants defined in `resume_helper.py` to use the ids of the Google docs you will use for your resume template and your cover letter template in `RESUME_DOCUMENT_ID` and `COVERLETTER_DOCUMENT_ID`, respectively.
1. Run the application by calling `python resume_helper.py <name of company to which you're applying> <title of role to which you are applying>`.

## _Caveat Emptor_

1. This has not been broadly tested. Special characters in the company name or title may cause issues.
1. This is written to solve my particular pain point and not for broad adoption, reuse, etc. I will not be responsible for injury, insult, frustration, sad feelings, or anything else which use, misuse, or failure of this script to do what you expect may cause you.

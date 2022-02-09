# NewtownsAtticRobot
This is the repository for the Autonomous Delivery Solutions remotely controlled rover.

This repository is for use with git.
Where you see <> symbols in this guide, you can remove them. They are variable placeholders

Below is a step by step of how to get access and modify the code:

1. Create a github account and tell me the email address or username associated with the account so I can add you for access

2. Download and install some sort of git interface, you can use a gui, like Fork, or you can just use terminal git which is also easy.
https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

3. clone the repository. instructions here:
	https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository

4. create a new local branch to begin working, usually somthing like "$ git branch <new-branch-name> <base-branch>"

So for us it will be 
$ git branch <new-branch-name> main
https://www.git-tower.com/learn/git/faq/create-branch


5. Edit the code with your changes, then add the files to the staged commit, then commit to the local branch you created. Commands will be like this:

git add filename.py filename2.py
git commit -m "Added gui to filename and made filename2 run more efficiently"

https://www.git-tower.com/learn/git/commands/git-commit

6. Push your changes to the remote branch, AKA the internet. be careful not to push to main!

git push <remote-branch-name> <local-branch-name>

https://www.atlassian.com/git/tutorials/syncing/git-push

7. if you think your code should be added to the main code, go to https://github.com/cam1255/NewtownsAtticRobot and make a pull request. 
Make sure you select the correct branches that you want to merge!
at the top left drop down, "base:" should be main, and "compare:" should be your branch name

8. Do not complete a pull request unless someone has fully reviewed your code!

9. Feel free to ask me any questions!

-Cameron

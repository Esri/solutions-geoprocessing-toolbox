Esri welcomes contributions from anyone and everyone. Please see our [guidelines for contributing](https://github.com/esri/contributing).

## How you can contribute code to this repository

### Make a new branch in the repo
Start contributing to the *solutions-geoprocessing-toolbox* repo by making a branch. Make a new branch from **dev** on github.com: 

Select the **dev** drop down
Type a new branch name. The convention uses your initials and a title separated by dashes "-". For example: *xy-new-suitabilty-tool*

![Create new branch](./img/CreateNewBranchDialogScreenshot.png)

*Fetch* and *merge* the new branch from the **Esri** remote: [Getting Changes from the repo](#getting-changes-from-the-repo).

Then checkout your new branch:

`git checkout <new_branch>`


### Getting Changes from the repo
The solutions-geoprocessing-toolbox repo changes without notice, so make sure you are getting the latest updates often.

Using git command line check your *remote*:

`> git remote -v`

This command should return a list of remotes including:

`Esri	https://github.com/Esri/solutions-geoprocessing-toolbox.git (fetch)`
`Esri	https://github.com/Esri/solutions-geoprocessing-toolbox.git (push)`

Then *fetch* the changes from the Esri remote:

`> git fetch Esri`

And *merge* the changes into the target branch: 

`> git merge Esri/<target branch>`

This will get your new branch from the repo.

### Share Your Mods
If you've made changes to the repo that you want to share with the community.

* Commit your changes
* Sync local with your remote
* Make a **Pull Request** from your remote fork on github.com ![New Pull Request](./img/NewPullRequestButtonIcon.png)


### Notes On Contributing
* Always work in the **dev** branch, never in *master*. This helps us keep our releases clean.
* Never merge Pull Requests. The [Repository Owner](#repository-owner) needs to test any updates to make sure the repo is stable.
* Always log an [Issue](https://github.com/Esri/solutions-geoprocessing-toolbox/issues) for problems you find, though you should check through the existing issues to make sure it wasn't already logged. 


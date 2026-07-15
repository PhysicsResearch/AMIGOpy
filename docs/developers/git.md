# GIT


![YouTube Video](https://img.youtube.com/vi/x_3NA-_Rjwo/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=x_3NA-_Rjwo)

# Git tutorial

Developers are strongly encouraged to watch the video and use sourcetree for version control

Working on the GUI

- Use the main branch when adding GUI elements like buttons and widgets.

- Switch to the main branch using Sourcetree, make your changes, and commit them immediately (multiple commits are encouraged).

- After committing, switch back to your feature branch and pull the latest changes from the main branch.

- This workflow minimizes conflicts because multiple users may be working on the same files with tools like the designer.

Staying Up-to-Date in Your Branch

- Before you begin coding in your own branch—whether at the start of each day or several times throughout the day—always pull the latest changes from the main branch into your branch.

- This practice ensures that you are working on the most current version of the code, which helps prevent divergent parallel versions and merge conflicts.

Merging Critical Changes

- Merge any changes that could affect others (for example, modifications to functions used by multiple team members) into the main branch as soon as possible.

- Notify your team if these changes are significant, ensuring that everyone is working with the updated functions.

Commit Often

- There is no limit on the number of commits—commit every change, even minor ones.

- Treat each commit as a snapshot of your work that can be easily reversed. Reverting small changes is much simpler than undoing large blocks of code, which may require additional manual fixes.

Use Descriptive Commit Messages

- Write clear, concise commit messages that summarize the changes you’ve made.

- Good commit messages help your team understand the purpose of the change and simplify debugging and code reviews later on.

Feature Branch Workflow

- Create separate branches for new features, bug fixes, or experiments.

- By isolating your work from the main branch, you ensure that the main branch remains stable until your changes are fully tested and reviewed.
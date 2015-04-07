# Nicely written code is good code.

The Python files in the TOMCAT scripts repository should conform to coding standards.
This makes the code easier to read and understand and much easier to maintain.

The code should at least conform to [PEP 8](https://www.python.org/dev/peps/pep-0008/), the Style Guide for Python Code, have consistend indentaion and a common file header.
We should also use [PyLint](http://www.pylint.org/) for code checks and try to keep our coding standards up.

# Minimum requirements
## Common file header
All Python files should start like with `#!/usr/bin/env python` and define their coding on the second line.
The following [docstring](https://www.python.org/dev/peps/pep-0257/) should contain the script name as well as the name and email of the coding person.
The rest of the docstring should quickly explain what the script generally does.
After that you can start with the import statements of the script.

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ReplaceProjections.py | David Haberthür <david.haberthuer@psi.ch>

Script to iteratively test rotation centers.
Calls 'gridrec_zp_64' on gws-2 with a range on rotation centers.
Renames the reconstructed slices and calls fiji so one can look at the
differently reconstructed slices in a stack.
"""

import ...
```

# Code health
The BitBucket repository is (manually) mirrored to [GitHub](https://github.com/habi/tomcat), where with each commit to the `master` branch a check of the *code health* on [landscape.io](https://landscape.io/github/habi/TOMCAT) is started.
This means, that even if you refuse to check your code with `pep8`, you can take a look at some errors and omissions in the code and correct for them.
Please do this!

# Useful git features
[Git](http://git-scm.com/) makes it ridiculously easy to test new things with your code while parts of it are still in perfect working condition.
This is called *branching* in git.
We're describing here an idea that is heavily based on the blog post [A successful Git branching model](http://nvie.com/posts/a-successful-git-branching-model/) of Vincent Driessen.

The idea is that there should be a *very* stable master branch which should always be available to users.
From this we should branch off a development branch in which the actual development happens.
New features should be developed in a 'new-feature'-branch.

Vincent Driessen made a graphic which shows all of the above in one overview.
It's available [here](http://nvie.com/files/Git-branching-model.pdf).

That means, if you'd like to test something new from the current state of the repository, for example to teach pigs to fly.

You would then generate a new branch and immediately switch to it

> git branch -b flying-pigs

To see what branches are availabe in the repository, you can use

> git branch
    > * flying-pigs
    > master

You would then program the new feature, commit, change, test, test, change, document and test again, all while commiting often to the flying-pigs branch.
Once you're done, you'd then do a final commit

> git commit -m "New feature done"

And switch back to the master branch of the repository with

> git checkout master

Merge all your changes *without* fast-forwarding.

> git merge --no-ff new-feature

This is *important*, because otherwise all the commits for the new feature would otherwise be squashed into one and potentially be lost.
With the `--no-ff` flag, all the commits are kept in the history.

Vincent Driessen made a nice graphic on it, which is linked below

![Merging with and without fast forwarding](http://nvie.com/img/2010/01/merge-without-ff.png)

At this stage you can now safely delete the merged branch and push the originating master branch to the remote repository.

> git branch -d new-feature

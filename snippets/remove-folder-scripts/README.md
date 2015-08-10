# Remove a bunch of folders in one go.

After the users left it is sometimes good to remove files not immediately needed anymore, to free up space on the file system.
Files than can safely removed immediately are the folders

- `viewrec` 
- `sin*`
- `cpr*`
- `fltp*`

since they can be regenerated easily.

If we are really desperate on file system space, once can also remove the reconstructions folders, e.g. the folders starting with `rec_*`.
The bash scripts in this subfolder do exactly this.
They REMOVE all those folders in all subfolders from which the script is called on.
They also warn you first.

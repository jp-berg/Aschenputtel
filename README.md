# aschenputtel
> Die guten ins Töpfchen, die schlechten ins Kröpfchen.

`aschenputtel` is a small program to manage files. At the moment it will delete files with suffix X that have no eqivalent files with suffix Y in another folder. There are two examples to clarify what I mean by that (those examles are also my primary use cases):

1. My camera records each photo I take as a '.DNG'-file and as a '.jpeg'-file. Since even a simple '.DNG'-preview takes forever to load, I filter out obvious-garbage-shots out by reviewing the '.jpeg'-files and deleting the bad ones. After that I have to manually delete all '.DNG's that do not have a '.jpeg'-equivalent anymore. What a pain! But now I am able to simply run `aschenputtel --source-file-suffix .jpeg --target-file-suffix .DNG $PHOTO_DIR` and my problem is solved.

2. I store the music I buy as '.flac'-files, but use '.opus'-files for playback on my smartphone / ~~mp3~~opus-player / laptop. If I want to delete files in the '.flac'-"world"  I have to manually mirror those changes across all music-library instances. What a pain! But running `aschenputtel --source-file-suffix .flac --target-file-suffix .opus --target $OPUS_DIR $FLAC_DIR` solves this problem for me.

There are probably other programs that do the exact same thing but better, but I like the exercise.

## Developement

`aschenputtel` is tested against Python 3.9, 3.10, 3.11, 3.12 and 3.13 on Linux.

The easiest way to start developement is to set up [uv](https://docs.astral.sh/uv/), install [nox](https://nox.thea.codes/en/stable/) and run `nox` in the folder of the cloned directory. This will set up the dev environment, clean the code and run the tests.



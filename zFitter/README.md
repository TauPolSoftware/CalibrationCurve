# ZFITTER642

 ZFITTER homepage:
 http://www-zeuthen.desy.de/theory/research/zfitter/

# Installation, e.g., on Linux:

 * download the distribution file zfitr6_42.tgz into an empty subdirectory zfitr642
 * `cd zfitr642`
 * `unpack by running gtar -xvzf zfitr6_42.tgz`
 * complile and link the test program
   `g77 -g  -fno-automatic -fdollar-ok -fno-backslash -finit-local-zero -fno-second-underscore -fugly-logint -ftypeless-boz  *.f -o zfitr642.exe`

 * run the testprogram and save the log file
   `./zfitr642.exe > zfitr642.log`

 * compare with the original log and check for differences:
   `diff original.log zfitr642.log`


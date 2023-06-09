
<img src="support/omni_icon.png" alt="Omniscient AI wearing headphones" width="50%">

# Welcome to Unmixer

<img src="support/screenshot.png" alt="Screenshot of UnMixer GUI">

Unmixer unmixes music.  It will take a recording of multiple instruments playing concurrently and with varying degrees of quality, extract the vocals, drum, bass, piano, electric guitar, acoustic guitar, synthesizer, strings and winds.

Unmixer is nothing more (or less) than a GUI frontend for LALAL.AI's AI-powered stem-splitting technology.

### Why UnMixer

If you don't use UnMixer, you either need to use [lalal.ai's website](https://lalal.ai/), where you have to upload the file repeatedly for each track you want to extract, or lalal's python program, [lalalai_splitter](https://github.com/OmniSaleGmbH/lalalai), where you also have to run the program and upload the file repeatedly for each track you want to extract, or [my version](https://github.com/lehenbauer/lalalai) of the python program, lalali_splitter, which will only upload the file once and do all of the splitting in one run, and can also avoid downloading unwanted backing tracks or downloading backing tracks without the corresponding stems.

It's pretty cool, but that python command line is kind of daunting.  You need to tell it the input file, the output directory, the stems you want, the backing tracks you want, the filter and model settings, and your API key.

UnMixer gives you a nice graphical interface to do all that.

Unmixer is not associated with LALAL.AI, just a personal project to help make music tools more accessible to musicians and composers.

### Fees for lalal.ai

LALAL.AI costs money, and you need to register and get an API key.  They currently charge $15 for 90 minutes, $50 for 300 minutes or $70 for 550 minutes.  They run sales fairly often and they have big discounts for bulk pricing.  Their most expensive tier without discounts is about 17 cents per minute; prices fall rapidly if you buy larger minute increments, as little as 6 cents per minute.

You pay by the minute, per stem/backing track combo.  That is, it costs no more to get the stem and backing track for one part than to get just one of the two.

So for example if you wanted to extract five parts from a four-minute song, you will be charged for 20 minutes.

### Requirements

It currently runs on Macs with reasonably current MacOS. It ought to be able to be ported to Windows and/or Linux.  I am not taking that on at this time but will entertain pull requests if someone is motivated to make it work.

### How To Install It

Go to the latest release at https://github.com/lehenbauer/unmixer/releases and download the .dmg file.

Open the .dmg file and drag the UnMixer icon to the Applications folder.

Unmount the dmg file by clicking on the eject icon next to it in Finder.

Drag the dmg file to the Trash.

### How To Run It

Double-click on the UnMixer icon.  UnMixer is unsigned so your MacOS might be configured to where it doesn't allow it to run.  If MacOS gives you a security warning and doesn't want to launch it, control-click on it and select "Open" and then from the security warning you can approve running it.  MacOS will remember this permission and you won't have to do it the next time you open the app.

If you'd like, you can change the overall security settings in System Preferences.  I'll leave the exercise of figuring that out to you.

You will need to acquire an API key from lalal.ai and paste it into the API Key field in UnMixer, and hit Save.  The key should be 16 characters and consist of only digits and the letters 'abcdef'.  Once saved it will be recalled in future runs of UnMixer.

Pick the song file you want to extract stems and/or backing tracks for by hitting "Pick" next to "Input File".  It can be a .wav or .aif, .mp3, and a lot of other formats.

Pick the folder you want to save extracted stems and/or backing tracks to by hitting "Pick" next to "Save to".  The save-to folder is also sticky so it will recalled across future runs of Unmixer.

Click on all the stems and backing tracks that you want to extract.  Remember that if you pick a stem or backing track, there is no charge to get the corresponding backing track or stem for the same instrument.

When you're all set, click Run.  UnMixer will show its status in the Status area and the status of the individual extractions as they move through being processed and then downloaded.

An indicator next to the Status area will slowly move left and right to show that it's doing something.

A "debug" window will also be updated with various status messages as they are sent by the application while it's working.

If all goes well, the status will conclude with "All Done." and all your stems and backing tracks should be present in your Save-to folder.

### How to Uninstall

Drag UnMixer from your Applications folder to the Trash.

### developers developers developers developers

If you are interested in banging on UnMixer, clone the repo and have at it.  Chreck out the make targets in the Makefile to get what's going on.

Create a python virtual environment with something like `python -m venv unmixenv` that has wheel, black, the latest pip, and whatever I missed that it complains about, and activate it with something like `. unmixenv/bin/activate`.  If none of this makes sense to you need to study up on python, python virtual environments, etc, before taking this on.

To run the program from the command line, `python3 UnMixer.py`  This can be handy versus an icon launch because you might see more of what's going on in the event of a failure.

To build the release, `make build`.

to build the disk image, you'll need the [homebrew package manager](https://brew.sh) (and to install homebrew, you'll need Xcode -- but don't worry, it's free.)

Once you've got brew up and running, install the create-dmg package by running `brew install create-dmg`.

After you've got a build, `make dmg` should make UnMixer.dmg in the top directory of UnMixer.

Image2Icons was used to make the icon.icns

Don't use conda as the source of python et al when building the app because the UnMixer app it produces won't run.

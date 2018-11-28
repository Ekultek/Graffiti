#!/bin/bash

function install {
    home="$HOME/.graffiti";
    exec_dir="$home/.install/bin";
    copy_dir="$home/.install/etc";
    exec_filename="$exec_dir/graffiti";
    mkdir -p $home $exec_dir $copy_dir;
    chmod +x ./graffiti.py;
    echo "starting file copying..";
    rsync -drq . $copy_dir;
    echo "creating executable";
    cat << EOF > $exec_filename
#!/bin/bash

#
# this is the graffiti executable file created by the installer
# this file was created on $(date +%F)
#

cd $copy_dir
exec python graffiti.py \$@
EOF
    echo "editing file stats";
    chmod +x $exec_filename;
    echo "export PATH=\"$PATH:$exec_dir\"" >> $HOME/.bash_profile;
    echo "installed, you need to run: source ~/.bash_profile";
}

install;
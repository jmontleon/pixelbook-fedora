RED='\033[0;31m'
NC='\033[0m' # No Color
if [ "$(whoami)" == "root" ]; then
  echo -e "${RED}"
  echo "You should not run this script as root, but as your normal user."
  echo "Ansible will escalate privileges when needed."
  echo "If you want to continue, anyway, then press any key."
  echo "Otherwise, press CTRL+C"
  echo -e "${NC}"
  read REPLY
fi

echo -e "${RED}WARNING: While this script has been tested, there may be edge cases which have not been accounted for. For your own protection, please ensure you have file backups and/or a disk image backup (such as using CloneZilla) of your machine before running this script.${NC}"

echo "Press a key to continue"
read REPLY

echo "Updating before running ansible (you may be prompted for sudo password)"

sudo dnf update -y || exit 1

sudo dnf install -y ansible dnf-plugins-core curl unzip git gpg || exit 1

echo "Running ansible. Press a key to start."
echo "When prompted for \"BECOME password\", use your sudo password, or leave blank if you have passwordless sudo"
echo ""
ansible-playbook playbook.yml -i hosts -K -e "login_user=$USER" $@ && \
echo -e "You should now reboot to make the changes active. ${RED}NOTE${NC} sometimes it takes a few reboots for the changes to activate"

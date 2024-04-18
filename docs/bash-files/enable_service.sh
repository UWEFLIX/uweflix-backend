echo "Reloading systemd"
systemctl --user daemon-reload
# shellcheck disable=SC2086
systemctl --user enable dashboard.service
# shellcheck disable=SC2086
systemctl --user start dashboard.service
# shellcheck disable=SC2086
systemctl --user status dashboard.service
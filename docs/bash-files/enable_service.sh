echo "Reloading systemd"
systemctl --user daemon-reload
# shellcheck disable=SC2086
systemctl --user enable uweflix-backend.service
# shellcheck disable=SC2086
systemctl --user start uweflix-backend.service
# shellcheck disable=SC2086
systemctl --user status uweflix-backend.service
# System Report Example

Generate system status reports using shell commands - no API keys required.

## Structure

```
system-report/
├── templates/
│   └── system-report.md.j2   # Main report template
├── snippets/
│   └── footer.md             # Report footer
├── context/
│   └── report.yaml           # Configuration & thresholds
└── output/
    └── system-report.md
```

## Usage

```bash
# Generate system report
mdcomp render templates/system-report.md.j2 \
  -c context/report.yaml \
  --snippets snippets \
  -o output/system-report.md

# Quick report without config
mdcomp render templates/system-report.md.j2 \
  --snippets snippets

# Disable certain sections
mdcomp render templates/system-report.md.j2 \
  --snippets snippets \
  --var sections='{"docker": false, "git_repos": false}'

# Custom disk thresholds
mdcomp render templates/system-report.md.j2 \
  --snippets snippets \
  --var thresholds='{"disk_warning": 70, "disk_critical": 85}'
```

## Features

### System Information
- OS version, architecture, uptime
- Installed tool versions (Python, Node.js, etc.)

### Disk Monitoring
- Disk usage with configurable warning thresholds
- Visual indicators (✅ healthy, ⚡ warning, ⚠️ critical)

### Network Status
- Active network interfaces
- Listening ports with associated processes

### Git Repository Status
- Find repos in current directory tree
- Show branch, uncommitted changes, last commit time

### Docker Status
- Running containers
- Disk usage by Docker

### Process Monitoring
- Top CPU consumers
- Top memory consumers

## Customization

### Add more tools to version check

Edit the "Environment Summary" section in the template:

```jinja
| **cargo** | {{ shell("cargo --version 2>/dev/null | awk '{print $2}'") | trim or 'Not installed' }} | {% if shell("which cargo 2>/dev/null") | trim %}✅{% else %}❌{% endif %} |
```

### Add custom sections

```jinja
{% if sections.custom_check %}
## My Custom Check

{{ shell("my-custom-script.sh") }}
{% endif %}
```

### Schedule regular reports

```bash
# Crontab entry for daily reports
0 9 * * * cd /path/to/system-report && mdcomp render templates/system-report.md.j2 --snippets snippets -o "output/report-$(date +\%Y\%m\%d).md"
```

## Platform Notes

This example is designed for macOS/Linux. Some commands may need adjustment for other platforms:

| Command | macOS | Linux |
|---------|-------|-------|
| `sw_vers` | ✅ | ❌ (use `lsb_release`) |
| `ifconfig` | ✅ | ✅ (or `ip addr`) |
| `lsof` | ✅ | ✅ |

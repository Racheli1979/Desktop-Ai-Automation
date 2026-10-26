# 🤖 Desktop AI Automation

An AI-powered Windows desktop application that automates work tracking and meeting preparation using Python, OpenAI, and Google Calendar.

## 📋 Overview

Desktop AI Automation consists of a launcher and two independent agents.

### ⏱️ Agent 1 — Work Tracker

- Tracks desktop activity and application usage.
- Monitors user activity and idle time.
- Records work-related data in an Excel file.
- Helps organize and review work hours.

### 🧠 Agent 2 — AI Meeting Assistant

- Retrieves upcoming meetings from Google Calendar.
- Uses OpenAI to classify meeting importance.
- Identifies meetings that require preparation.
- Automatically prepares the desktop for important meetings according to configured rules.

## 🛠️ Technology Stack

- **Python**
- **OpenAI API**
- **LangChain**
- **Google Calendar API**
- **Model Context Protocol (MCP)**
- **PyInstaller**
- **Inno Setup**
- **Windows Credential Manager**
- **Excel**

## 💻 Requirements

For the packaged Windows application, users do not need to install Python or the development dependencies separately.

Users need:

- A supported Windows computer.
- An internet connection for OpenAI and Google Calendar integration.
- A valid OpenAI API key.
- A Google account with access to Google Calendar.

## 📦 Installation

1. Download `DesktopAiAutomation-Setup.exe` from the application's official distribution location.
2. Double-click the installer.
3. Follow the installation wizard.
4. Keep the default installation directory or select another available location.
5. Complete the installation.
6. Launch **Desktop AI Automation** from the desktop shortcut or the Start menu.

The application is installed by default in:

```text
C:\Program Files\DesktopAiAutomation
```

Administrator approval may be required during installation, depending on the Windows configuration.

## ⚙️ First-Time Setup

### 🔑 1. Configure the OpenAI API Key

When the Meeting Assistant is launched, the application prompts the user to enter an OpenAI API key if one has not already been configured for the current Windows user.

1. Obtain an API key through the OpenAI Platform.
2. Enter the key when prompted.
3. The application stores the key in Windows Credential Manager using the `keyring` library.

The API key is stored separately for each Windows user. It is not intended to be included in the installer.

OpenAI API usage may incur charges depending on the account and usage.

### 📅 2. Authorize Google Calendar Access

When Google Calendar access is required for the first time:

1. The application initiates the Google OAuth authorization process.
2. Follow the authentication flow and sign in to the intended Google account.
3. Review and approve the requested permissions.
4. Complete the authorization process.

The application uses the configured Google Calendar read-only scope to retrieve meeting information.

The user's OAuth token is stored locally and separately from the application installation files.

## ▶️ Running the Application

Launch the application using the desktop shortcut or the Start menu.

- **First manual launch:** The launcher starts Agent 1 in the background and configures it to start automatically when the current Windows user signs in. Agent 2 also starts.
- **Windows sign-in:** Agent 1 starts automatically. Agent 2 does not start automatically.
- **Subsequent manual launches:** The launcher checks whether Agent 1 is already running to avoid starting another instance, then starts Agent 2.

Some actions depend on the configured agents, available network access, valid credentials, and upcoming calendar events.

## 💾 Data Storage

Application files and user data are stored separately.

### 📁 Application Installation

```text
C:\Program Files\DesktopAiAutomation
```

Contains the launcher, both agent executables, bundled dependencies, and supporting application files.

### 🗂️ User Data

```text
%LOCALAPPDATA%\DesktopAiAutomation
```

This directory is used for user-specific data, including:

- Google Calendar OAuth token.
- Work-tracking Excel file.
- Application logs.

The OpenAI API key is stored separately in Windows Credential Manager.

Keeping user data outside the installation directory helps preserve it when application files are updated or replaced.

## 🔒 Security and Privacy

- Each user should configure their own OpenAI API key.
- Each user should authorize their own Google account.
- Personal API keys and OAuth tokens must not be committed to source control or included in public releases.
- The Google OAuth client configuration is distinct from a user's personal OAuth token.
- User-specific data should remain in the user's local application data directory.

## 🩺 Troubleshooting

If the application does not start or a service connection fails:

- **🔑 OpenAI:** Verify your API key and internet connection.
- **📅 Google Calendar:** Verify your internet connection and complete the Google authorization process if prompted.
- **⚠️ Application errors:** Check the application logs at `%LOCALAPPDATA%\DesktopAiAutomation\logs\`, if this is the configured log directory.

## 👩‍💻 Development

To work with the source code, clone the repository:

```bash
git clone https://github.com/Racheli1979/Desktop-Ai-Automation.git
cd Desktop-Ai-Automation
```

Create and activate a virtual environment, install the project's dependencies according to its dependency files, and run the automated tests:

```bash
python -m pytest
```

The packaged Windows release is built using PyInstaller and distributed through an Inno Setup installer.
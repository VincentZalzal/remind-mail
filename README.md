# remind-mail
A python program that sends emails (using an external SMTP server) according to recurring events described in a YAML file. Can then be scheduled as a cron job or in Windows Task Scheduler.

## How to setup Windows Task Scheduler

1. **Create Task**
2. Set **Configure for** to **Windows 10**
3. Add multiple triggers at different times:
   - **Daily**
   - **Delay task**: **5 minutes**
   - **Stop Task**: **30 minutes**
4. Add an action:
   - **Start a program**
   - `C:\Windows\System32\wscript.exe`
   - Argument: `remind-mail.vbs`
   - Start in the `remind-mail` folder (full path, no trailing backslash)
5. In **Settings**:
   - Change the stop after duration to **30 minutes**
   - Change the rule when already running to **Stop the existing instance**
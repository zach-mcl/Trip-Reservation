# Steps to Build & Run:
_This assumes that you already have Git installed on your machine. The following steps align with MacOS, since that's what I'm using. Adjust accordingly. For any issues, reach out to me and I'll help._

---
#### 1. Navigate where you want the folder to appear
Do this in a new terminal window. You don't have to make a new folder or anything, this is just so you know where the project folder will be for step 3.
```bash
cd ~/Desktop
```

#### 2. Clone the repo (using terminal)
```bash
git clone https://github.com/jacqueline-welch/Trip-Reservation
```

#### 3. Open folder in terminal
Go to the Desktop (or wherever you put it), find the folder (named **Trip-Reservation**), then right-click on it and click 'New Terminal at Folder'

#### 3. Build the docker image
The name can be whatever. It might take a sec to download the stuff in the requirements.txt file.
```bash
docker build -t tripresapp .
```

#### 4. Run the Docker Container
Just name the container, keep the image name at the end the same as in the last step.
```bash
docker run -p 5001:5001 --name tripresapp-container tripresapp
```

#### 5. Access Application
In Docker Desktop, click the **5001:5001** under the Port(s) section to open the app in your browser.

---
### _Note: For testing purposes, the admin logins are as follows:_
> | Username | Password |
> | -------- | -------- |
> | admin1 | 12345 |
> | admin2 | 24680 |
> | admin3 | 98765 |

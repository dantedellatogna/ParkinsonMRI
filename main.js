const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");  // ✅ FIXED: Now path is defined
const { spawn } = require("child_process"); 


let mainWindow;

app.whenReady().then(() => {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 720,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"), // ✅ Secure IPC
            contextIsolation: true,
        },
        autoHideMenuBar: true,
    });

    mainWindow.loadFile("index.html");
});

// ✅ Fix: File selection using Electron's dialog
ipcMain.handle("select-file", async () => {
    const result = await dialog.showOpenDialog({
        properties: ["openFile"],
        filters: [{ name: "NIfTI Files", extensions: ["nii", "nii.gz"] }],
    });
    return result.filePaths; // Return selected file paths (array)
});

// ✅ Fix: Python Inference Handling
ipcMain.handle("run-inference", async (event, filePath) => {
    try {
        const { spawn } = require("child_process");
        const python = spawn("python", ["backend.py"]);

        console.log("Running inference on:", filePath);

        const inputData = JSON.stringify({ file_path: filePath });

        let output = "";
        let errorOutput = "";

        python.stdout.on("data", (data) => {
            output += data.toString();
        });

        python.stderr.on("data", (data) => {
            errorOutput += data.toString();
        });

        return new Promise((resolve, reject) => {
            python.on("close", (code) => {
                console.log("Python process exited with code:", code);
                if (errorOutput) {
                    console.error("Python Error Output:", errorOutput);
                }

                try {
                    const jsonStart = output.indexOf("{");
                    const jsonEnd = output.lastIndexOf("}");
                    if (jsonStart !== -1 && jsonEnd !== -1) {
                        const jsonString = output.substring(jsonStart, jsonEnd + 1);
                        const result = JSON.parse(jsonString);
                        resolve(result);  // ✅ Ensure the result is returned
                    } else {
                        throw new Error("Invalid JSON response");
                    }
                } catch (err) {
                    console.error("Error parsing JSON:", err);
                    reject({ error: "Invalid JSON response" });
                }
            });

            python.stdin.write(inputData + "\n");
            python.stdin.end();
        });
    } catch (err) {
        console.error("Error running inference:", err);
        return { error: "Failed to execute script" };
    }
});

ipcMain.handle("get-nifti-slices", async (event, filePath) => {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn("python", [
        path.join(__dirname, "nifti2img.py"),
        filePath,
      ]);
  
      let dataBuffer = "";
  
      pythonProcess.stdout.on("data", (data) => {
        dataBuffer += data.toString();
      });
  
      pythonProcess.stderr.on("data", (data) => {
        console.error(`Python error: ${data}`);
      });
  
      pythonProcess.on("close", (code) => {
        try {
          const result = JSON.parse(dataBuffer);
          if (result.error) {
            reject(result.error);
          } else {
            resolve(result.slices);
          }
        } catch (error) {
          reject("Failed to parse Python output");
        }
      });
    });
  });
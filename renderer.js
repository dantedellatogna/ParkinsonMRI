const selectFileButton = document.getElementById("fileInput");
const runInferenceButton = document.getElementById("runInference");

selectFileButton.addEventListener("click", async () => {
    const filePaths = await window.electron.invoke("select-file");
    
    if (!filePaths || filePaths.length === 0) {
        alert("No file selected.");
        return;
    }

    document.getElementById("selectedFile").innerText = filePaths[0]; // Display selected file
    selectFileButton.dataset.filePath = filePaths[0]; // Store file path
});

runInferenceButton.addEventListener("click", async () => {
    const filePath = selectFileButton.dataset.filePath;

    if (!filePath) {
        alert("Por favor, selecciona un archivo NIfTI (.nii o .nii.gz).");
        return;
    }

    try {
        const result = await window.electron.invoke("run-inference", filePath);
        console.log("Resultado recibido:", result);

        if (!result || result.error) {
            throw new Error(result?.error || "Respuesta inválida del backend");
        }

        document.getElementById("result").innerText = result.Diagnosis;
        document.getElementById("output").innerText = result.Output.toFixed(4);
    } catch (error) {
        console.error("Error en la inferencia:", error.message);
        document.getElementById("result").innerText = "Error al procesar el archivo.";
        document.getElementById("output").innerText = "-";
    }
});


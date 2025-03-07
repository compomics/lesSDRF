const path = require('path')
const { app, BrowserWindow, ipcMain } = require('electron')
const treeKill = require('tree-kill');


let streamlitProcess = null

function startStreamlit() {
    console.log('startStreamlit')
    streamlitProcess = require('child_process').spawn(
        path.join(__dirname, '/dist/streamlitWrapper'), { windowsHide: false })
}

const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 600
    })
    startStreamlit()
    
    win.loadURL('http://localhost:8501');
    // if(process.env.NODE_ENV === 'development') {
    //     win.loadURL('http://localhost:5173');
    // } else {
    //     console.log(__dirname)
    //     win.loadFile(path.join(__dirname, '/build/frontend/index.html'))
    //     startFastAPI()
    // }
}

const stopStreamlit = () => {
    if (streamlitProcess !== null) {
        treeKill(streamlitProcess.pid)
        streamlitProcess = null
    }
}

app.on('before-quit', stopStreamlit)

app.whenReady().then(() => {
    createWindow()
     app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
    
})

app.on('window-all-closed', () => {
    console.log(process.platform)
    // for not macOS
    if (process.platform !== 'darwin') {
        app.quit()
    }
})
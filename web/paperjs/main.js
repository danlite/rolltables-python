import { drawGrid } from './grid.js'

paper.install(window)
window.onload = () => {
    paper.setup('grid')
    drawGrid()
}

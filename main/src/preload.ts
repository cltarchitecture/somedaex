import fs from 'fs'
import mmap from '@raygun-nickj/mmap-io'

function getMemoryMappedFile (path: string): Buffer {
  path = path.toString()
  const fd = fs.openSync(path, 'r')
  const size = fs.fstatSync(fd).size
  const buffer = mmap.map(size, mmap.PROT_READ, mmap.MAP_SHARED, fd, 0)
  return buffer

  // Potential resource leak:
  // Does mmap know to close the file descriptor when it's done?
}

(global as {[_: string]: any}).getMemoryMappedFile = getMemoryMappedFile

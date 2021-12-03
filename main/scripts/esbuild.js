const esbuild = require('esbuild')

/**
 * @type {import('esbuild').BuildOptions}
 */
const config = {
  entryPoints: [
    'src/main.ts',
    'src/preload.ts'
  ],
  bundle: true,
  outdir: 'build',
  platform: 'node',
  external: ['@raygun-nickj/mmap-io', 'electron'],
  tsconfig: 'tsconfig.json'
}

esbuild.build(config).then((result) => {
  console.log(result)
}).catch((failure) => {
  console.log(failure)
  process.exit()
})

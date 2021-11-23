const esbuild = require('esbuild')

/**
 * @type {import('esbuild').BuildOptions}
 */
const config = {
  entryPoints: [
    'main/src/main.ts',
    'main/src/preload.ts'
  ],
  bundle: true,
  outdir: 'main/build',
  platform: 'node',
  external: ['@raygun-nickj/mmap-io', 'electron'],
  tsconfig: 'main/tsconfig.json'
}

esbuild.build(config).then((result) => {
  console.log(result)
}).catch((failure) => {
  console.log(failure)
  process.exit()
})

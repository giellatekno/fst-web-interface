import precompileIntl from "svelte-intl-precompile/sveltekit-plugin";

const print = console.log;

print("hey");

function compile_locales() {
    let _ws;

    function configureServer({ config, ws, watcher, moduleGraph }) {
        print(config);
        _ws = ws;
        watcher.on("change", file => {
            print("file changed");
            ws.send({ type: "message", message: "file changed" });
        });
    }

    function resolveId(source, importer) {
        _ws.send({ type: "message", message: "hey there" });
        print("hey there!");
    }

    function load(id) {
        print(id);
        // returns something
    }
    function transform(content, id) {
        // returns something
    }

    return {
        name: "custom-compile-locales",
        enforce: "pre",
        configureServer,
        resolveId,
    }
}

/** @type {import('@sveltejs/kit').Config} */
export default {
  kit: {
    target: '#svelte',
    vite: {
      plugins: [
        compile_locales(),
        // if your translations are defined in /locales/[lang].js
        precompileIntl('intl', "$intl"),
        // precompileIntl('locales', '$myprefix') // also you can change import path prefix for json files ($locales by default)
      ]
    }
  }
};

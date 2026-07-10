const vm = require("vm");

let script = "";
process.stdin.setEncoding("utf-8");
process.stdin.on("data", (chunk) => {
  script += chunk;
});
process.stdin.on("end", () => {
  try {
    const sandbox = {};
    sandbox.window = sandbox;
    sandbox.self = sandbox;
    sandbox.document = { getElementsByTagName: () => [], querySelector: () => null };
    vm.createContext(sandbox);
    vm.runInContext(script, sandbox, { timeout: 5000 });
    process.stdout.write(JSON.stringify(sandbox.__NUXT__ ?? null));
  } catch (err) {
    process.stderr.write(String((err && err.stack) || err));
    process.exit(1);
  }
});

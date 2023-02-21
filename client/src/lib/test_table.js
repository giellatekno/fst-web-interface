import { Table } from "./table.js";

const _fmt = `
-|A | B|C|
a|
b|
c|
d|
`;
const t = Table.from_format(_fmt, "tittel");
t.data.set(0, 0, "hei");
t.data.set(2, 2, "moi");

console.log(`${t}`);
console.log(t.as_console_str());
console.log("==========================================");

const t_without = t.without_empty_columns_and_rows();
console.log(`${t_without}`);
console.log(t_without.as_console_str());

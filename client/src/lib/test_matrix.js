import { Matrix } from "./matrix.js";

const a = new Matrix(4, 3);
//for (let i = 0; i < 4; i++) {
//    for (let j = 0; j < 3; j++) {
//        twod.set(i, j, (i + 1)*(j + 1) + (j + 1));
//    }
//}
a.set(0, 0, "a");
a.set(2, 2, "c");

console.log("a:", a.str());
console.log(a.as_console_str());
console.log();

//const transposed = a.transpose();
//console.log("transposed:", transposed.str());
//console.log(transposed.as_console_str());
//console.log();

const { matrix: a_without } = a.without_empty_columns_and_rows();
console.log("a_without:", a_without.str());
console.log(a_without.as_console_str());

//const transposed_without = transposed.without_empty_columns_and_rows();
//console.log("transposed_without:", transposed_without.str());
//console.log(transposed_without.as_console_str());

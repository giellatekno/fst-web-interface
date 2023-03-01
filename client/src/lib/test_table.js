import { Table, group_by_length, reverse_spans } from "./table.js";
import { is_equal } from "./utils.js";

///*
const _fmt = `
-| Indicative | Conditional | Imperative | Potential | 
-| Prs | Prt  |  something  |     D      |         E |
a|
b|
c|
d|
`;
const t = Table.from_format(_fmt, "tittel");
t.data.set(0, 0, "hei");
t.data.set(2, 2, "moi");

//console.log(`${t}`);
console.log(t.as_console_str({ show_caption: false }));
console.log("\nwithout_empty_columns_and_rows:\n");

const t_without = t.without_empty_columns_and_rows();
//console.log(`${t_without}`);
console.log(t_without.as_console_str({ show_caption: false }));
//*/

/*
const _fmt = `
a | b | c | d
`;
const t = Table.from_format(_fmt, "tittelen");
t.data.set(0, 0, "A");
t.data.set(0, 2, "C");
console.log(t.as_console_str({ show_caption: false }));
console.log("####");
console.log(t.without_empty_columns_and_rows().as_console_str({ show_caption: false }));
//*/

function test_group_by_length1() {
    const input1 = "\nabcd\nefgh\nxx\nyy\n\n";
    const actual1 = group_by_length(input1);
    const expected1 = [ ["abcd", "efgh"], ["xx", "yy"] ];
    if (!is_equal(actual1, expected1)) throw new Error("Test failed");
}

function test_group_by_length2() {
    const input2 = "\nabcde\n\nefghe\nokoko\nxxx\nyy\n\nzz";
    const actual2 = group_by_length(input2);
    const expected2 = [ ["abcde", "efghe", "okoko" ], ["xxx"], ["yy", "zz"] ];
    if (!is_equal(actual2, expected2)) throw new Error("group by length 2 failed");
}

function test_all_group_by_length() {
    test_group_by_length1();
    test_group_by_length2();
}

function test_reverse_spans() {
    const input1 = [ [1, 1, 1] ];
    const actual1 = reverse_spans(input1);
    //console.log(actual1);
}

//*
(function () {
    //test_all_group_by_length();
    test_reverse_spans();
})();
//*/


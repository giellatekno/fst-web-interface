import { Matrix } from "./matrix.js";
import { enumerate } from "./utils.js";

function reverse_spans(spans) {
    // TODO solve this in general
    if (spans[0] === 1 && spans[1] === 1) {
        // [1, 1] -> [1, 1]
        return [1, 1];
    } else if (spans[0] === 1 && spans[1] === 2) {
        // [1, 2] -> [2, 1]
        return [2, 1];
    } else if (spans[0] === 2 && spans[1] === 1) {
        // [2, 1] -> [1, 2]
        return [1, 2];
    } else {
        throw Error("unhandled case");
    }
}

class MisalignedError extends Error {
    constructor(row, column, char, ...params) {
        super(...params);
        this.name = this.constructor.name;
        this.message = `Mis-aligned column in row ${row}. `
            + `Because "|" was found in this column on line 1, expected `
            + `"|" to be found in column ${column} but, but found ${char}.`;
    }
}

function group_by_length(lines) {
    let current_len = lines[0].length;
    let current_group = [lines[0]];
    const groups = [];
    for (let line of lines.slice(1)) {
        if (line.length !== current_len) {
            // this line's length is different, so make next group
            current_len = line.length;
            groups.push(current_group);
            current_group = [];
        }
        current_group.push(line);
    }
    if (current_group.length > 0) {
        groups.push(current_group);
    }
    return groups;
}

/*
  make_table()
    take string format input (as shown below), and turn it into a structure
    like this:
let table = {
    caption: "caption",
    row_headers: ["1", "2"],
    columns: [
        [{text: "A", span: 1}, { text: "B", span: 2}, {text: "C", span: 1}],
        [{text: "_a", span: 1}, { text: "_b1", span: 1 }, {text: "_b2", span:1}, {text: "c", span:1}],
    ],
    data: [
        ["a", "b"],
        ["c", "d"],
    ],
};
*/

export class Table {
    #data;

    constructor(caption, data, row_headers, columns) {
        this.caption = caption;
        this.data = data;
        this.row_headers = row_headers;
        this.columns = columns;
    }

    without_empty_columns_and_rows() {
        const {
            matrix: new_data,
            kept_rows,
            kept_cols,
        } = this.data.without_empty_columns_and_rows();

        this.data = new_data;

        //console.log(changed_rows);
        console.log("kept_cols:");
        console.log(kept_cols);

        console.log("columns");
        console.log(this.columns);
        // columns:
        // [
        //   [{..}, {..}, {..}],
        //   [{..}, {..}, {..}],    in my example: this is the longest
        // ]
        const new_columns = Array(this.columns.length).fill(null).map(_ => []);
        console.log(new_columns);

        // "pointers" into how far we currently are in the
        // `this.columns` array of arrays
        const indexes = Array(this.columns.length).fill(0);

        // kept_cols = { 0: 0, 1: 1 }
        for (let [new_col, old_col] of Object.entries(kept_cols)) {
            // this loop: [0, 0], [1, 1]
            // TODO but will it be in rising order? that is from index 0 first,
            // then index 1, then the next, etc..

            const to_push = [];
            for (let i = 0; i < this.columns.length; i++) {
                let found = 0;
                for (let x = 0; x < this.columns[i].length; x++) {
                    found += this.columns[i][x].span;
                    if (found === old_col) {
                    }
                }
                // this.columns[i][old_col]
                // THAT'S NOT NECESSARILY TRUE
            }

            {
                    text: "...",
                    span: -1,
            }

            for (let i = 0; i < to_push.length; i++) {
                new_columns[i].push(to_push);
            }
        }
    }

    static from_format(format, caption = null) {
        const lines = format.split("\n").filter(line => line.trim().length > 0);

        let [col_headers, row_headers] = group_by_length(lines);
        row_headers = row_headers
            .map(s => s.trim().replaceAll("|", ""))
            .filter(s => s.length > 0);

        const col_header_height = col_headers.length;
        const col_header_width = col_headers
            .map(ch => ch.split("|"))
            .reduce((prev, cur) => Math.max(prev, cur.length), 0);

        const data = new Matrix(col_header_width + 2, row_headers.length + 2);

        const columns = Array(col_header_height).fill(0).map(_0 => []);

        let last_index = 0;
        const first_col_row = col_headers[0];
        for (let [i, ch] of enumerate(first_col_row)) {
            if (ch !== "|") {
                continue;
            }

            const first_col = first_col_row.slice(last_index, i);
            const to_be_pushed = [first_col];

            // find the other headers
            for (let j = 1; j < col_headers.length; j++) {
                const ch_other = col_headers[j][i];
                if (ch_other !== ch) {
                    throw new MisalignedError(j + 1, i, ch_other);
                }

                let other_col = col_headers[j].slice(last_index, i);
                to_be_pushed.push(other_col);
            }

            const to_be_pushed_splits = to_be_pushed.map(s => s.split("|"));
            const spans = to_be_pushed_splits.map(arr => arr.length);
            const rev_spans = reverse_spans(spans);

            for (let [t, arr] of enumerate(to_be_pushed_splits)) {
                for (let inner_idx = 0; inner_idx < arr.length; inner_idx++) {
                    columns[t].push({
                        text: arr[inner_idx],
                        span: rev_spans[t],
                    });
                }
            }

            last_index = i + 1;
        }

        return new Table(caption, data, row_headers, columns);
    }
}

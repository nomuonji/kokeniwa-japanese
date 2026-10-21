const assert = require('node:assert/strict');
const grid = require('../site/static/fans.js');
// Published guide examples must agree with the tool; manufacturer capacities
// deliberately describe a different arrangement, not this grid.
assert.equal(grid(280, 210, 57, 0, 0).count, 12);
assert.equal(grid(280, 210, 75, 0, 0).count, 6);
assert.equal(grid(278, 210, 57, 0, 0).count, 12);
assert.equal(grid(285, 114, 57, 0, 0).count, 10);
assert.equal(grid(285, 114, 58, 0, 0).count, 4);
assert.equal(grid(120, 120, 57, 3, 0).count, 4);
assert.equal(grid(120, 120, 57, 3, 4).count, 1);
assert.equal(grid(280, 210, 57, 0, 200).count, 0);
assert.equal(grid(100, 100, 500, 0, 0).count, 0);
assert.equal(grid(2000, 2000, 1, 0, 0).count, 4000000);
assert.equal(grid(300.3, 200.2, 100.1, 0, 0).count, 6);
for (const value of [NaN, Infinity, -1, 0, 2001]) {
  assert.throws(() => grid(value, 210, 57, 0, 0), RangeError);
}
console.log('Badge grid: guide examples, fit boundaries, decimals and bounds OK');

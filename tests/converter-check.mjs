import assert from 'node:assert/strict';
import converter from '../js/narzedzia.js';

const { convertUnit, formatConverted, energyFactors, massFactors } = converter;
assert.equal(convertUnit(1, 'MWh', 'MJ', energyFactors), 3600);
assert.equal(convertUnit(1, 'GJ', 'kWh', energyFactors), 277.77777777777777);
assert.equal(convertUnit(1, 'kcal', 'kWh', energyFactors), 4.1868 / 3600);
assert.equal(formatConverted(convertUnit(1, 'kg', 't', massFactors)), '0,001');
assert.equal(formatConverted(convertUnit(1, 'g', 'kg', massFactors)), '0,001');
assert.equal(formatConverted(convertUnit(1, 'g', 't', massFactors)), '0,000001');
assert.equal(formatConverted(convertUnit(1, 'kWh', 'GJ', energyFactors)), '0,0036');
console.log('Przelicznik jednostek: wszystkie sprawdzenia zakończone poprawnie.');

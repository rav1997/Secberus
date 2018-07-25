'use strict';
const request = require('org/arangodb/request')
const url = require('../constant')
try {
  var argv = module.context.argv
  var response = request.post(url.PROCESSOR_BASE+'cis/run/', {
    form: {
      account_id: argv[0].account_id,
      service: argv[0].service,
    }
  });
} catch(e) {
  response = e
  throw e
}
module.exports = response

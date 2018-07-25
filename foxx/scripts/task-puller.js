'use strict';
const request = require('org/arangodb/request')
const url = require('../constant')
try {
  var argv = module.context.argv
  var response = request.post(url.PULLER_BASE+'pull/', {
    form: {
      external_id: argv[0].external_id,
      role_arn: argv[0].role_arn,
      service: argv[0].service,
      user_id: argv[0].user,
      interval_id: '',
    }
  });
} catch(e) {
  response = e
  throw e
}
module.exports = response

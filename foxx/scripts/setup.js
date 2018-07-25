'use strict';
const db = require('@arangodb').db;

const jobs = 'Jobs';
if (!db._collection(jobs)) {
  db._createDocumentCollection(jobs);
}

const external_id = 'AwsExternalIds';
if (!db._collection(external_id)) {
  db._createDocumentCollection(external_id);
}

const roles = 'Roles';
if (!db._collection(roles)) {
  db._createDocumentCollection(roles);
}

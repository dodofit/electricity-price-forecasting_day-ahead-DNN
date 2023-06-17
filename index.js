/* HTTP Cloud Function.
*
* @param {Object} req Cloud Function request context.
* @param {Object} res Cloud Function response context.
*/
exports.make_predictions = (req, res) => {
  res.send('Make predictions for day-ahead electricity prices using a DNN.');
};

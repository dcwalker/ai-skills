function formatWeekHeader(weekStart) {
  const start = new Date(weekStart);
  const end = new Date(start);
  end.setDate(start.getDate() + 6);
  return `Week of ${start.toDateString()} – ${end.toDateString()}`;
}

module.exports = { formatWeekHeader };

/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import {
  QueryFormData,
  QueryObject,
  buildQueryContext,
  ensureIsArray,
} from '@superset-ui/core';

export default function buildQuery(formData: QueryFormData) {
  const {
    start_time,
    end_time,
    y_axis,
    series,
    tooltip_columns,
    tooltip_metrics,
    order_by_cols,
  } = formData;

  const groupBy = ensureIsArray(series);
  const orderby = ensureIsArray(order_by_cols).map(
    expr => JSON.parse(expr) as [string, boolean],
  );
  const columns = Array.from(
    new Set([
      start_time,
      end_time,
      y_axis,
      ...groupBy,
      ...ensureIsArray(tooltip_columns),
      ...orderby.map(v => v[0]),
    ]),
  );

  return buildQueryContext(formData, (baseQueryObject: QueryObject) => [
    {
      ...baseQueryObject,
      columns,
      metrics: ensureIsArray(tooltip_metrics),
      orderby,
      series_columns: groupBy,
    },
  ]);
}

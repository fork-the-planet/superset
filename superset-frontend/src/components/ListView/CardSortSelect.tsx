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
import { useState, useMemo } from 'react';
import { styled, t } from '@superset-ui/core';
import { FormLabel, Select } from '@superset-ui/core/components';
import { SELECT_WIDTH } from './utils';
import { CardSortSelectOption, SortColumn } from './types';

const SortContainer = styled.div`
  display: inline-flex;
  font-size: ${({ theme }) => theme.fontSizeSM}px;
  align-items: center;
  text-align: left;
  width: ${SELECT_WIDTH}px;
`;

interface CardViewSelectSortProps {
  onChange: (value: SortColumn[]) => void;
  options: Array<CardSortSelectOption>;
  initialSort?: SortColumn[];
}

export const CardSortSelect = ({
  initialSort,
  onChange,
  options,
}: CardViewSelectSortProps) => {
  const defaultSort =
    (initialSort &&
      options.find(
        ({ id, desc }) =>
          id === initialSort[0].id && desc === initialSort[0].desc,
      )) ||
    options[0];

  const [value, setValue] = useState({
    label: defaultSort.label,
    value: defaultSort.value,
  });

  const formattedOptions = useMemo(
    () => options.map(option => ({ label: option.label, value: option.value })),
    [options],
  );

  const handleOnChange = (selected: { label: string; value: string }) => {
    setValue(selected);
    const originalOption = options.find(
      ({ value }) => value === selected.value,
    );
    if (originalOption) {
      const sortBy = [
        {
          id: originalOption.id,
          desc: originalOption.desc,
        },
      ];
      onChange(sortBy);
    }
  };

  return (
    <SortContainer>
      <Select
        ariaLabel={t('Sort')}
        header={<FormLabel>{t('Sort')}</FormLabel>}
        labelInValue
        onChange={handleOnChange}
        options={formattedOptions}
        showSearch
        value={value}
        data-test="card-sort-select"
      />
    </SortContainer>
  );
};

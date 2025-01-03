
queries = {
    # Query 1
    '1. Duplicate data in 09_payable_file': '''
        select 
        merged,
        count(merged)
        from
        `fynd-db.Outstanding.09_Payable_File_table` as A
        group by
        1
        having
        count(merged) <> 1
    ''',

    '2. Checking already paid data showing in outstanding file': '''
        select 
        merged,
        paid_settled_merged_transaction,
        REGEXP_CONTAINS(paid_settled_merged_transaction, CONCAT(r'(^|,)', merged, r'(,|$)')) as cc1,
        from
        `fynd-db.Outstanding.09_Payable_File_table` as A
        where
        REGEXP_CONTAINS(paid_settled_merged_transaction, CONCAT(r'(^|,)', merged, r'(,|$)')) <> false
    ''',


    '3. Checking return transaction not having sale transaction': '''
        select
        bag_id,
        paid_settled_merged_transaction,
        count(bag_id) as bag_count,
        from
        `fynd-db.Outstanding.09_Payable_File_table` 
        where
        bag_id in
        (select 
        bag_id,
        -- merged,
        -- paid_settled_merged_transaction,
        -- REGEXP_CONTAINS(paid_settled_merged_transaction, CONCAT(r'(^|,)', merged, r'(,|$)')) as cc1,
        from
        `fynd-db.Outstanding.09_Payable_File_table` as A
        where
        transaction_type = 'Return'
        and paid_settled_merged_transaction is null)
        group by
        1,2
        having
        count(bag_id) = 1 
        order by
        1 asc
            ''',


    '4. Checking old data inserted in 09_net_collection table': '''
        SELECT 
            A.bag_id, 
            A.collection_partner, 
            A.Settlement_type, 
            A.inserted_date, 
            B.bag_id, 
            B.Transaction_type, 
            C.bag_id, 
            C.settlement_type, 
            D.bag_id
        FROM 
            `fynd-db.finance_recon_tool_asia.01_finance_avis_data_final` AS A
        LEFT JOIN 
            `fynd-db.finance_dwh.Brand_Settlement_pulse` AS B 
            ON A.bag_id = B.bag_id
        LEFT JOIN 
            `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily` AS C 
            ON A.bag_id = C.bag_id
        LEFT JOIN 
            `fynd-db.finance_recon_tool_asia.05_partner_collection` AS D 
            ON A.bag_id = D.bag_id
        WHERE 
            A.Settlement_type <> 'NA' 
            and date(A.inserted_date) > '2024-07-31'
            AND B.bag_id IS NOT NULL 
            AND C.bag_id IS NOT NULL 
            AND D.bag_id IS NOT NULL
            AND (
                CASE 
                    WHEN A.Settlement_type = 'collection' THEN 'Sale'
                    WHEN A.Settlement_type = 'refund' THEN 'Return'
                    ELSE 'Claim'
                END
            ) = B.Transaction_type
        GROUP BY 
            1,2,3,4,5,6,7,8,9
            ''',


    '5. Checking whether expected payout date is null': '''
        SELECT
        *
        FROM
        `fynd-db.Outstanding.09_Payable_File_table`
        where
        expected_payout_date is null
            ''',

    '6. Validation for seller net collection formula': '''
        SELECT
        distinct
        bag_id,
        transaction_type,
        settlement_type,
        round(esp-seller_discounts-bca,0) BCA_Diff,
        round(bca-seller_tender_value-tcs_on_vog-tds_on_bca+seller_fees-seller_net_collection,0) Seller_net_collection_diff
        FROM
        `fynd-db.Outstanding.09_Payable_File_table`
        where
        round(esp-seller_discounts-bca,0) not in (0,1)
        and round(bca-seller_tender_value-tcs_on_vog-tds_on_bca+seller_fees-seller_net_collection,0) not in (0,1)
            ''',

    '7. Checking sign for payout, refund & claim ': '''
        SELECT
        *,
        CASE 
            WHEN (settlement_type = 'collection' AND bca >= 0) THEN 'MATCH'
            WHEN (settlement_type = 'refund' AND bca <= 0) THEN 'MATCH'
            WHEN (settlement_type = 'Claim' AND bca >= 0) THEN 'MATCH'
            ELSE 'NOT MATCH'
        END AS comment
        FROM
        `fynd-db.Outstanding.09_Payable_File_table`
        WHERE
        --settlement_type ='collection' and
        settlement_type in ('collection','refund','cliam') and
        NOT (
            (settlement_type = 'collection' AND bca >= 0) 
            OR 
            (settlement_type = 'refund' AND bca <= 0)
            OR 
            (settlement_type = 'claim' AND bca >= 0)
            )
            ''',

    '8. Checking TCS & TDS': '''
        SELECT
        distinct
        bag_id,
        settlement_type,
        segement_code,
        tcs_on_vog,
        tds_on_bca,
        case when segement_code not in ('FY','UN') and tcs_on_vog = 0 then 'Match'
        when segement_code not in ('FY','UN') and tds_on_bca = 0 then 'Match'
        when segement_code in ('FY','UN') and tcs_on_vog <> 0 and tds_on_bca <> 0 then 'Match' else "Not Match" end as Check
        FROM
        `fynd-db.Outstanding.09_Payable_File_table`
        where
        (case when segement_code not in ('FY','UN') and tcs_on_vog = 0 then 'Match'
        when segement_code not in ('FY','UN') and tds_on_bca = 0 then 'Match'
        when segement_code in ('FY','UN') and tcs_on_vog <> 0 and tds_on_bca <> 0 then 'Match' else "Not Match" end) = 'Not Match'   
            ''',


    '9. Collection done but data not updated in 09_net_collection': '''
        with status as (SELECT
        Company_id,
        Company_name,
        Bagid,
        Placed_date,
        Cancelled_date,
        bag_invoiced,
        RTO_delivered_date,
        Delivered_date,
        FROM
        `fynd-db.finance_asia_dwh.Bag_Audit_review`),
        error_bags as (
        SELECT
        bag_id
        FROM `fynd-db.finance_recon_tool_asia.03_error_view_data`
        WHERE
            resolve_date is null
        )
        SELECT
        DISTINCT
        C.Company_id,
        C.Company_name,
        A.bag_id AS COLLECTED_BAG,
        B.bag_id AS SETTLEMENT_BAG,
        D.bag_id AS error_BAG,
        A.order_type,
        Placed_date,
        Cancelled_date,
        bag_invoiced,
        RTO_delivered_date,
        Delivered_date
        FROM
        `fynd-db.finance_recon_tool_asia.05_partner_collection` AS A
        left join
        (SELECT
        DISTINCT
        bag_id
        FROM  `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily` 
        WHERE
        Settlement_type = 'collection'
        ) AS B
        ON
        A.bag_id = B.bag_id
        left join
        status as C
        on
        A.bag_id = C.Bagid
        left join
        error_bags as D
        on
        A.bag_id = D.bag_id
        WHERE
        receipt_date >= '2023-04-01'
        and net_remitted <> 0
        and C.Company_id not in (select
        test_company
        from `fynd-db.finance_dwh.test_details`)
        AND B.bag_id IS NULL
        and Delivered_date is not null
        AND D.bag_id IS NULL
                    ''',

    '10. Refund done but data not updated in 09_net_collection': '''
        with status as (SELECT
        Company_id,
        Company_name,
        Ordering_channel,
        Bagid,
        Placed_date,
        Cancelled_date,
        bag_invoiced,
        RTO_delivered_date,
        Delivered_date,
        Return_picked_date,
        Return_delivered_date
        FROM
        `fynd-db.finance_asia_dwh.Bag_Audit_review`),
        error_bags as (
        SELECT
        bag_id
        FROM `fynd-db.finance_recon_tool_asia.03_error_view_data`
        WHERE
            resolve_date is null
        )
        SELECT
        DISTINCT
        C.Company_id,
        C.Company_name,
        C.Ordering_channel,
        A.bag_id AS COLLECTED_BAG,
        B.bag_id AS SETTLEMENT_BAG,
        D.bag_id AS error_BAG,
        A.order_type,
        Placed_date,
        Cancelled_date,
        bag_invoiced,
        RTO_delivered_date,
        Delivered_date,
        Return_picked_date,
        Return_delivered_date
        FROM
        `fynd-db.finance_recon_tool_asia.05_partner_refunds` AS A
        left join
        (SELECT
        DISTINCT
        bag_id
        FROM  `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily` 
        WHERE
        Settlement_type = 'refund'
        ) AS B
        ON
        A.bag_id = B.bag_id
        left join
        status as C
        on
        A.bag_id = C.Bagid
        left join
        error_bags as D
        on
        A.bag_id = D.bag_id
        WHERE
        refund_date >= '2023-04-01'
        and net_refunded <> 0
        and C.Company_id not in (select
        test_company
        from `fynd-db.finance_dwh.test_details`)
        AND B.bag_id IS NULL
        and C.Company_id not in (507)
        and (case when Ordering_channel in ('FYND','UNIKET') and Return_picked_date is not null then 'yes'
        when Ordering_channel not in ('FYND','UNIKET') and Return_delivered_date is not null then 'yes' else 'no' end) = 'yes'
        AND D.bag_id IS NULL  
            ''',


    '11. Checking for duplicate count in 09_net_collection': '''
        select
        concat(bag_id,Settlement_type) as Merged,
        count(concat(bag_id,Settlement_type))
        from `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily`
        group by
        1
        having  
        count(concat(bag_id,Settlement_type)) not in (1)
            ''',

    '12. Checking for presence of Non-RBL, Prepaid & Fynd/Uniket in 09_payable_file': '''
        select 
        *
        from
        `fynd-db.Outstanding.09_Payable_File_table` A
        where
        order_type = 'PPD'
        and
        ordering_channel not in ('UNIKET', 'FYND')
        and
        A.Company_Type = 'Non RBL'
        and collection_comment = 'collection_pending'
            ''',

    '13. Checking for difference in collection': '''
        select 
        *,
        current_timestamp() as table_update_date
        from
        `fynd-db.Outstanding.09_Payable_File_table`
        where
        Collection_amount_comment = 'collection_diff'
            '''
}
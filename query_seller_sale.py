queries = {
    "query_seller_net_data": """
    WITH seller_net_data AS (
        SELECT
            company_id,
            company_name,
            ordering_channel,
            segement_code,
            sales_channel,
            settlement_model,
            settlement_model_code,
            order_type,
            order_date,
            fiscal_year,
            bag_id,
            settlement_type,
            recon_status,
            return_window_date,
            payout_window_date,
            expected_payout_date,
            sett_no,
            sett_id,
            mrp,
            seller_discounts,
            store_discount_amount,
            bca,
            product_gst_perc,
            round(vog,2) as vog,
            tds_on_bca,
            tcs_on_vog,
            seller_fees,
            seller_tender_value,
            round(seller_net_collection,2) as seller_net_collection,
            ROUND(mrp - seller_discounts - store_discount_amount,2) AS bca_cc,
            ROUND(bca - (mrp - seller_discounts - store_discount_amount),2) AS diff_bca_cc,
            ROUND((mrp - seller_discounts - store_discount_amount) * 100 / (100 + ABS(product_gst_perc)), 2) AS vog_cc,
            ROUND(vog - ROUND((mrp - seller_discounts - store_discount_amount) * 100 / (100 + ABS(product_gst_perc)), 2),2) AS diff_vog_cc,

            -- TDS calculation logic
            CASE 
                WHEN segement_code IN ("FY", "UN") AND DATE(order_date) >= '2024-10-01' THEN 
                    ROUND((mrp - seller_discounts - store_discount_amount), 2) * 0.001
                WHEN segement_code IN ("FY", "UN") AND DATE(order_date) < '2024-10-01' THEN 
                    ROUND((mrp - seller_discounts - store_discount_amount), 2) * 0.01
                ELSE 0
            END AS tds_cc,

            -- TCS calculation logic
            CASE 
                WHEN segement_code IN ("FY", "UN") AND DATE(order_date) >= '2024-07-10' THEN 
                    ROUND((mrp - seller_discounts - store_discount_amount) * 100 / (100 + ABS(product_gst_perc)), 2) * 0.005
                WHEN segement_code IN ("FY", "UN") AND DATE(order_date) < '2024-07-10' THEN 
                    ROUND((mrp - seller_discounts - store_discount_amount) * 100 / (100 + ABS(product_gst_perc)), 2) * 0.01
                ELSE 0
            END AS tcs_cc
        FROM 
            `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily`
        WHERE
            expected_payout_date BETWEEN "{start_date}" AND "{end_date}"
    ),

    -- Subquery to count occurrences of each bag_id and concatenation of bag_id and settlement_type
    bag_con_count_data AS (
        SELECT
            bag_id,
            settlement_type,
            COUNT(*) AS bagg_count,
            CONCAT(bag_id, settlement_type) AS bag_settlement_concat,
            COUNT(CONCAT(bag_id, settlement_type)) AS bag_settlement_concat_count  -- Count of concatenated values
        FROM
            seller_net_data
        GROUP BY
            bag_id, settlement_type
    )

    -- Final query
    SELECT
        sd.*,
        ROUND((tds_cc - tds_on_bca), 2) AS diff_tds,
        ROUND((tcs_cc - tcs_on_vog), 2) AS diff_tcs,
        ROUND((mrp - seller_discounts - store_discount_amount - seller_tender_value + seller_fees),2) AS seller_sale_cc,
        ROUND(((mrp - seller_discounts - store_discount_amount - seller_tender_value + seller_fees) - tds_cc - tcs_cc),2) AS seller_net_cc,
        ROUND(((mrp - seller_discounts - store_discount_amount - seller_tender_value + seller_fees) - tds_cc - tcs_cc - seller_net_collection), 2) AS net_diff_cc,
        CONCAT(sd.bag_id, ",") AS conccat,  -- Concatenated bag_id
        CONCAT(sd.bag_id, sd.settlement_type) AS bag_cc,  -- Bag ID with settlement type
        bcc.bagg_count AS bag_count,  -- Count of each bag_id and settlement type
        bcc.bag_settlement_concat AS bag_con,  -- Concatenated bag_id and settlement_type
        bcc.bag_settlement_concat_count AS bag_con_count,  -- Count of concatenated values
        CASE
            WHEN order_type = 'COD' THEN CONCAT(company_id, '_', segement_code, '_', settlement_model_code, '_', order_type, '_V')
            WHEN order_type = 'PPD' THEN CONCAT(company_id, '_', segement_code, '_', settlement_model_code, '_', order_type, '_C')
        END AS ledger_name
    FROM
        seller_net_data sd
    LEFT JOIN
        bag_con_count_data bcc
    ON
        sd.bag_id = bcc.bag_id AND sd.settlement_type = bcc.settlement_type;
    """,

    "query_brand_accounting_entries": """
    SELECT
        DENSE_RANK() OVER (ORDER BY expected_payout_date,company_id,VOUCHERTYPENAME,sales_channel,expected_payout_date,order_type ASC) entry_code,
        DATE,
        Mode,
        VOUCHERTYPENAME,
        Narration,
        DebitLedger,
        AmountDebitLedger,
        CreditLedger,
        AmountCreditLedger
    FROM (
        WITH
          Truth_table AS (SELECT * FROM `fynd-db.Brand_Accounting_Entries_Asia.Brand_Seller_Sale_FY25_Table`)
        SELECT
          expected_payout_date,
          format_date('%Y%m%d', expected_payout_date) as DATE,
          "Journal" as Mode,
          VOUCHERTYPENAME,
          CONCAT(Narration," for ", sales_channel, " for the period ",expected_payout_date ) AS Narration,
          entry_Type,
          order_type,
          A.segement_code,
          company_id,
          sales_channel,
          CASE WHEN seller_sales_amount > 0 AND B.ordering_channel IN ("FY", "FP", "FS", "UN", "OE","OM") AND entity = "seller" AND mop = "COD" THEN ledger_name WHEN seller_sales_amount > 0 AND B.ordering_channel IN ("FY", "FP", "FS", "UN", "OE","OM") AND entity = "seller" AND mop = "PPD" THEN ledger_name ELSE Credit_Ledger END AS DebitLedger,
          CASE WHEN seller_sales_amount > 0 THEN ROUND(seller_sales_amount*-1) ELSE ROUND(seller_sales_amount) END AS AmountDebitLedger,
          CASE WHEN seller_sales_amount < 0 AND B.ordering_channel IN ("FY", "FP", "FS", "UN", "OE","OM") AND entity = "seller" AND mop = "COD" THEN ledger_name WHEN seller_sales_amount < 0 AND B.ordering_channel IN ("FY", "FP", "FS", "UN", "OE","OM") AND entity = "seller" AND mop = "PPD" THEN ledger_name ELSE Credit_Ledger END AS CreditLedger,
          CASE WHEN seller_sales_amount < 0 THEN ROUND(seller_sales_amount)*-1 ELSE ROUND(seller_sales_amount) END AS AmountCreditLedger
        FROM 
          `fynd-db.Brand_Accounting_Entries_Asia.Seller_sale_Logic` AS A
        LEFT JOIN
          Truth_table as B
        ON
          A.segement_code = B.ordering_channel 
          AND A.entry_Type = B.Status
          AND A.order_type = B.mop
        WHERE
          order_type = 'COD'
          AND expected_payout_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY
          1,2,3,4,5,6,7,8,9,10,11,12,13,14
        ORDER BY 
          expected_payout_date,company_id,VOUCHERTYPENAME,sales_channel,order_type ASC
    )
    ORDER BY entry_code ASC
    """
}

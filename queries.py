
queries = {
    # Query 1
    '1. fynd-db.finance_recon_tool_asia.01_finance_avis_data_final': '''
        select
        bag_id,
        concat(bag_id,Recon_Status,Settlement_type,Transaction_Type) as Merged,
        count(concat(bag_id,Recon_Status,Settlement_type,Transaction_Type))
        from `fynd-db.finance_recon_tool_asia.01_finance_avis_data_final`
        group by
        1,2
        having count(concat(bag_id,Recon_Status,Settlement_type,Transaction_Type)) not in (1)
    ''',

    # Query 2
    '2. Seller fees date validation': '''
        select
        *
        from `fynd-db.finance_recon_tool_asia.11_seller_fees_daily`
        where
        invoice_generation_date is null
    ''',


    # Query 3
    # '3. Checking 01_finance all data inserted into 11_seller_fees': '''
    #     with commission as (select
    #     bag_id,
    #     Transaction_Type,
    #     Commission_in_percent
    #     from  
    #     `fynd-db.finance_recon_tool_asia.11_seller_fees_logic` 
    #     group by
    #     1,2,3
    #     )
    #     select
    #     A.company_id,
    #     A.company_name,
    #     A.ordering_channel,
    #     A.sales_channel,
    #     A.bag_id,
    #     A.transaction_type,
    #     A.recon_status,
    #     A.recon_date,
    #     A.return_window_date,
    #     A.payout_window_date,
    #     A.inserted_date,
    #     B.bag_id,
    #     B.transaction_type,
    #     C.Commission_in_percent
    #     from `fynd-db.finance_recon_tool_asia.01_finance_avis_data_final` as A
    #     left join
    #     `fynd-db.finance_recon_tool_asia.11_seller_fees_daily` as B
    #     on
    #     A.bag_id = B.bag_id
    #     and A.transaction_type = B.transaction_type
    #     left join
    #     commission as C
    #     on
    #     A.bag_id = C.bag_id
    #     and A.transaction_type = C.transaction_type
    #     where
    #     A.transaction_type not in ('NA','SLA')
    #     and B.bag_id is null 
    #     and A.recon_status not in ("return_bag_lost","bag_lost","dispute","dispute_R")
    #     and A.sales_channel not in ('JIOMART',"Freshpik")
    #     and A.company_id <> 3138
    #     -- and C.Commission_in_percent <> 0 
    #     group by
    #     1,2,3,4,5,6,7,8,9,10,11,12,13,14
    # ''',

    # Query 3
    '3. Transaction components validation': '''
        select
        bag_id,
        transaction_type,
        inserted_date,
        round(transaction_fee+packaging_fee+logistics_charges+refund_support_fees+sla_charges-net_charges,0) as diff
        from `fynd-db.finance_recon_tool_asia.11_seller_fees_daily`
        where
        round(transaction_fee+packaging_fee+logistics_charges+refund_support_fees+sla_charges-net_charges,0) not in (0,-1,-1)
        and inserted_date > '2023-09-30'
        group by 1,2,3, transaction_fee,packaging_fee,refund_support_fees,sla_charges,net_charges,logistics_charges
    ''',

    # Query 4
    '4. Transactions in net collection validation': '''
        select
        concat(bag_id,Settlement_type) as Merged,
        count(concat(bag_id,Settlement_type))
        from `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily`
        group by 1
        having  
        count(concat(bag_id,Settlement_type)) not in (1)
    ''',

    # Query 5
    '5. Transactions in seller fees validation': '''
        select
        bag_id,
        concat(bag_id,transaction_type) as Merged,
        count(concat(bag_id,transaction_type))
        from `fynd-db.finance_recon_tool_asia.11_seller_fees_daily`
        group by 1,2
        having  
        count(concat(bag_id,transaction_type)) not in (1)
    ''',


    # Query 6
    '6. Transactions in seller claims validation': '''
        select
        current_shipment_id,
        concat(current_shipment_id,transaction_type) as Merged,
        count(concat(current_shipment_id,transaction_type))
        from `fynd-db.finance_recon_tool_asia.12_seller_claims_daily`
        group by 1,2
        having  
        count(concat(current_shipment_id,transaction_type)) not in (1)
    ''',


    # Query 7
    '7. Aggregate liability validation': '''
        select
        *
        from `fynd-db.finance_recon_tool_asia.12_seller_claims_daily`
        where
        aggregate_liability is null
    ''',


    # Query 8
    '8. Lost claim validation': '''
        select
        *
        from `fynd-db.finance_recon_tool_asia.01_finance_avis_data_final` as A
        left join
        `fynd-db.finance_recon_tool_asia.12_seller_claims_daily` as B
        on
        A.current_shipment_id = B.current_shipment_id
        where
        A.claim_settle_date is not null
        and A.transaction_type = 'Claim'
        and A.dp_partner = 'fynd'
        and B.current_shipment_id is null
    ''',
    


    # Query 9
    '9. Gstin validation': '''
        select
        company_id,
        company_name,
        ordering_channel
        from `fynd-db.finance_recon_tool_asia.11_seller_fees_daily`
        where
        company_gstn is null
        group by
        1,2,3
    ''',



    # Query 10
    '10. Positive transaction components validation': '''
        SELECT
        CONCAT(bag_id,transaction_type,total_charges) AS Merged,
        FROM
        `fynd-db.finance_recon_tool_asia.11_seller_fees_daily`
        GROUP BY
        1
        HAVING
        COUNT(CONCAT(bag_id,transaction_type)) NOT IN (1)
    ''',


     # Query 11
    '11. Negative transaction components validation': '''
        select
        *
        from `fynd-db.finance_recon_tool_asia.11_seller_fees_daily`
        where
        transaction_type = 'Return'
        and net_charges < 0
    ''',


    # Query 12
    '12. GST Tag validation': '''
        select
        company_id,
        company_name,
        ordering_channel,
        company_gstn,
        gst_tag,
        case WHEN LENGTH(company_gstn) = 10 then "SGST"
        when SUBSTRING(company_gstn,1,2) = '27' then "SGST" else "IGST" end as Tag,
        case when gst_tag = (case WHEN LENGTH(company_gstn) = 10 then "SGST"
        when SUBSTRING(company_gstn,1,2) = '27' then "SGST" else "IGST" end) then "Match" else "Not_Match" end as CC
        from `fynd-db.finance_recon_tool_asia.11_seller_fees_daily`
        where
        (case when gst_tag = (case WHEN LENGTH(company_gstn) = 10 then "SGST"
        when SUBSTRING(company_gstn,1,2) = '27' then "SGST" else "IGST" end) then "Match" else "Not_Match" end) = "Not_Match"
        group by 1,2,3,4,5,6
    ''',

     # Query 13
    '13. 09_Net collection all data validation': '''
        select
        A.company_id,
        A.company_name,
        A.ordering_channel,
        A.bag_id,
        A.Settlement_type,
        A.recon_status,
        A.recon_date,
        A.inserted_date,
        B.bag_id,
        B.Settlement_type
        from `fynd-db.finance_recon_tool_asia.01_finance_avis_data_final` as A
        left join
        `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily` as B
        on
        A.bag_id = B.bag_id
        and A.Settlement_type = B.Settlement_type
        where
        A.Settlement_type not in ('NA','SLA')
        and A.recon_status in ('delivery_done','return_bag_delivered','return_bag_picked')
        and B.bag_id is null 
        and (case when A.Settlement_type = 'collection' and A.collection_partner = 'fynd' then 'yes' 
        when A.Settlement_type = 'refund' and A.refund_partner = 'fynd' then 'yes' else 'no' end) = 'yes'
        group by
        1,2,3,4,5,6,7,8,9,10
    ''',


     # Query 14
    '14. Net collection collection & refund validation': '''
        select
        bag_id,
        settlement_type,
        collection_partner,
        refund_partner,
        case when settlement_type in ('collection','Claim',"dispute","rectify","rectify_R") and collection_partner = 'fynd' then 'Yes' when settlement_type = 'refund' and refund_partner = 'fynd' then 'Yes' else 'No' end as Comment
        from `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily`
        where
        (case when settlement_type in ('collection','Claim',"dispute","rectify","rectify_R") and collection_partner = 'fynd' then 'Yes' when settlement_type = 'refund' and refund_partner = 'fynd' then 'Yes' else 'No' end) = 'No'
    ''',


    # Query 15
    '15. 09_Net collection collection & refund validation': '''
        select
        A.bag_id,
        B.bag_id,
        A.settlement_type,
        B.settlement_type,
        A.transaction_type,
        A.collection_partner,
        A.refund_partner,
        case when A.settlement_type = 'collection' and A.collection_partner = 'fynd' then 'Yes' when A.settlement_type = 'refund' and A.refund_partner = 'fynd' then 'Yes' else 'No' end as Comment
        from `fynd-db.finance_recon_tool_asia.01_finance_avis_data_final` as A
        left join
        `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily` as B
        on
        A.bag_id = B.bag_id 
        and A.settlement_type = B.settlement_type
        where
        A.settlement_type <> 'NA'
        and A.recon_status not in ("bag_lost","return_bag_lost")
        and (case when A.settlement_type = 'collection' and A.collection_partner = 'fynd' then 'yes' when A.settlement_type = 'refund' and A.refund_partner = 'fynd' then 'yes' else 'No' end) = 'yes'  
        and (case when A.transaction_type = 'Sale' and A.collection_partner = 'fynd' then 'Yes' when A.transaction_type = 'Return' and A.refund_partner = 'fynd' then 'Yes' when A.transaction_type = 'Claim' and A.collection_partner = 'fynd' then 'Yes' else 'No' end) = 'Yes'
        and B.bag_id is null
    ''',


    # Query 16
    '16. NA settlement validation': '''
        select
        *
        from `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily`
        where
        -- settlement_type = 'NA'
        (case when settlement_type in ('collection','Claim','rectify','rectify_R') and collection_partner = 'fynd' then 'Yes' when settlement_type = 'refund' and refund_partner = 'fynd' then 'Yes' else 'No'end ) = 'No'
    ''',


    # Query 17
    '17. Fynd collection placed bags validation': '''
        select
        A.bag_id,
        B.bag_id,
        A.order_type,
        A.transaction_type,
        case when B.settlement_type = 'collection' then 'Sale' else 'Return' end as transaction_type,
        from `fynd-db.finance_recon_tool_asia.11_seller_fees_daily` as A
        left join
        `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily` as B
        on
        A.bag_id = B.bag_id
        and A.transaction_type = (case when B.settlement_type = 'collection' then 'Sale' when B.settlement_type = 'refund' then 'Return' else 'NA' end )
        where
        transaction_type <> 'SLA'
        and (case when A.transaction_type = 'Sale' and A.collection_partner = 'fynd' then 'yes' when A.transaction_type = 'Return' and A.refund_partner = 'fynd' then 'yes' else 'no'end) = 'yes'
        and B.bag_id is null
    ''',


    # # Query 18
    # '18. PPD seller amount validation': '''
    #     select
    #     *
    #     from
    #     (SELECT
    #     *
    #     FROM
    #     `fynd-db.Outstanding.09_Payable_File`
    #     where
    #     expected_payout_date <= current_date()
    #     and order_type = "PPD"
    #     and lower(collection_partner) = "seller") as A
    #     left join
    #     (select
    #     bag_id,
    #     txn_id,
    #     collected_amount
    #     from
    #     `fynd-db.finance_recon_tool_asia.05_partner_collection`) as B
    #     on 
    #     A.bag_id = B.bag_id
    #     where
    #     B.bag_id is not null
    # ''',


     # Query 19
    '19. Checking sett_id count in payout process table': '''
        select
        sett_id,
        count(sett_id)
        from `fynd-db.finance_recon_tool_asia.payout_process_table`
        group by
        1
        having
        count(sett_id) <> 1
    ''',

      # Query 20
    '20. Checking bagwise payout report': '''
        select
        UTR,
        paid_amt,
        dispute,
        round(sum(Net_Payout),2) as payable,
        round(sum(Net_Payout)+dispute-paid_amt) as Diff
        from `fynd-db.finance_recon_tool_asia.Bag_Wise_Payout_Report`
        where
        UTR in (select
        utr_no
        from
        `fynd-db.finance_recon_tool_asia.14_seller_payouts_New`
        where
        sett_date > "2024-04-01" )
        group by
        1,2,3
        having Diff <> 0
    ''',

      # Query 21
    '21. Checking claimwise payout report': '''
        select
        SF_UTR,
        total_utr_paid,
        round(sum(claimable_amt),2),
        round(sum(claimable_amt)-total_utr_paid) as Diff
        from `fynd-db.finance_recon_tool_asia.Shipment_wise_Claim_UTR`
        where
        SF_UTR in ("_2414920231016000202198812",
        "_2414920231016000202197711",
        "_AXISCN0279665404",
        "_AXISCN0312196630",
        "_2414920231016000202198811")
        group by
        1,2
    ''',

    #  # Query 23
    # '23. Checking any settlement id is updated after the payment  ': '''
    #     select
    #     A.sett_id,
    #     sum(net_amount)as NA,
    #     case when NC is null then 0 else NC end as N,
    #     case when SF is null then 0 else SF end as S,
    #     case when MD is null then 0 else MD end as M,
    #     case when CL is null then 0 else CL end as C,
    #     round(sum(net_amount)-(case when NC is null then 0 else NC end)-(case when SF is null then 0 else SF end)-(case when MD is null then 0 else MD end)-(case when CL is null then 0 else CL end)) as diff
    #     from
    #     `fynd-db.finance_recon_tool_asia.13_seller_disbursement_payouts` as A
    #     left join
    #     (select
    #     sett_id,
    #     SUM(seller_net_collection) AS NC
    #     from
    #     `fynd-db.finance_recon_tool_asia.09_seller_net_collection_daily`
    #     GROUP BY
    #     1) as B
    #     on 
    #     A.sett_id = B.sett_id
    #     left join
    #     (Select
    #     sett_id,
    #     SUM(total_charges) as SF
    #     from
    #     `fynd-db.finance_recon_tool_asia.11_seller_fees_daily`
    #     GROUP BY
    #     1) as C
    #     on 
    #     A.sett_id = C.sett_id
    #     left join
    #     (Select
    #     sett_id,
    #     SUM(dispute_amount) as MD
    #     from
    #     `fynd-db.finance_recon_tool_asia.17_seller_manual_Dispute`
    #     GROUP BY
    #     1) as D
    #     on 
    #     A.sett_id = D.sett_id
    #     left join
    #     (Select
    #     sett_id,
    #     SUM(claimable_amt) as CL
    #     from
    #     `fynd-db.finance_recon_tool_asia.12_seller_claims_daily`
    #     GROUP BY
    #     1) as E
    #     on 
    #     A.sett_id = E.sett_id
    #     where
    #     payout_id in ("2250_OE_COD_19_SD_034_FY24",
    #     "2250_OE_COD_21_SD_034_FY24",
    #     "0292_FS_COD_AC_SD_034_FY24",
    #     "0517_OE_COD_AC_SD_034_FY24",
    #     "0042_OE_COD_05_SD_034_FY24",
    #     "0034_OM_COD_AC_SD_034_FY24",
    #     "0021_OE_COD_AC_SD_034_FY24",
    #     "0046_OE_COD_10_SD_034_FY24",
    #     "0442_OE_COD_07_SD_034_FY24",
    #     "0320_OE_COD_28_SD_034_FY24",
    #     "0046_OE_COD_13_SD_034_FY24",
    #     "0269_OE_COD_04_SD_034_FY24",
    #     "3557_OE_COD_AC_SD_034_FY24",
    #     "0025_FS_COD_AC_SD_034_FY24",
    #     "3523_FS_COD_AC_SD_034_FY24",
    #     "0320_OM_COD_AC_SD_034_FY24",
    #     "2467_OE_COD_AC_SD_034_FY24",
    #     "0680_UN_COD_MA_SD_034_FY24",
    #     "0021_FS_COD_AC_SD_034_FY24",
    #     "0442_FS_COD_AC_SD_034_FY24",
    #     "0046_FS_COD_AC_SD_034_FY24",
    #     "0046_OE_COD_14_SD_034_FY24",
    #     "0046_OE_COD_09_SD_034_FY24",
    #     "1076_OE_COD_17_SD_034_FY24",
    #     "0334_FS_COD_AC_SD_034_FY24",
    #     "0046_OE_COD_08_SD_034_FY24",
    #     "0334_OE_COD_06_SD_034_FY24",
    #     "2250_OE_COD_22_SD_034_FY24",
    #     "0002_FS_COD_AC_SD_034_FY24",
    #     "2411_OM_COD_AC_SD_034_FY24")
    #     group by
    #     1,3,4,5,NC,SF,MD,CL
    #     having
    #     round(sum(net_amount)-(case when NC is null then 0 else NC end)-(case when SF is null then 0 else SF end)-(case when MD is null then 0 else MD end)) <> 0
    # ''',

    # Query 22
    '22. Checking any old data inserted into new table': '''
        select
        A.bag_id,
        collection_partner,
        Settlement_type,
        inserted_date,
        B.bag_id,
        B.Transaction_type
        from `fynd-db.finance_recon_tool_asia.01_finance_avis_data_final` as A
        left join
        `fynd-db.finance_dwh.Brand_Settlement_pulse` as B
        on A.bag_id = B.bag_id
        and (case when Settlement_type = 'collection' then 'Sale'when Settlement_type = 'refund' then 'Return' else 'Claim' end) = B.Transaction_type
        where
        Settlement_type <> 'NA'
        and B.bag_id is not null
        group by
        1,2,3,4,5,6
    ''',

    # Query 23
    '23. Checking old lost claim check inserted into new table': '''
        select
        *
        from `fynd-db.finance_recon_tool_asia.01_finance_avis_data_final`
        where
        Bag_ID in (select
        Bag_ID
        from `fynd-db.finance_dwh.Brand_Lost_settlement`
        group by
        1)
        and transaction_type = 'Claim'
    ''',


     # Query 24
    '24. Checking duplicate count in bag_wise payout report ': '''
        with bag_count as 
        (select
        bag_id,
        transaction_type,
        concat(bag_id,transaction_type) as merged,
        count(concat(bag_id,transaction_type)) as bag_count
        from `fynd-db.finance_recon_tool_asia.Bag_Wise_Payout_Report`
        group by  
        1,2,3)
        
        select
        A.bag_id,
        company_id,
        company_name,
        Payment_Date,
        A.transaction_type,
        UTR,
        concat(A.bag_id,A.transaction_type) as merged,
        bag_count,
        seller_net_collection,
        total_charges,
        Net_Payout
        from `fynd-db.finance_recon_tool_asia.Bag_Wise_Payout_Report` as A
        left join
        bag_count as B
        on
        concat(A.bag_id,A.transaction_type) = B.merged
        where
        bag_count <> 1
        group by  
        1,2,3,4,5,6,7,8,9,10,11
        
    ''',


    # Seller sale validation query 

    


    # Add more queries as needed
}
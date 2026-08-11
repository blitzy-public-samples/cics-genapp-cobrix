******************************************************************
*  COPYBOOK  : GFTXR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : TX
******************************************************************
 01  RT-FTX-RATING.

          03 RT-FTX-TERRITORY-CODE            PIC X(3).
          03 RT-FTX-CLASS-CODE                PIC X(4).
          03 RT-FTX-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FTX-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FTX-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FTX-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FTX-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FTX-RATED-PREMIUM             PIC 9(9)V9(2).

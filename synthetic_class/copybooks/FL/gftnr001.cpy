******************************************************************
*  COPYBOOK  : GFTNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : TN
******************************************************************
 01  RT-FTN-RATING.

          03 RT-FTN-TERRITORY-CODE            PIC X(3).
          03 RT-FTN-CLASS-CODE                PIC X(4).
          03 RT-FTN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FTN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FTN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FTN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FTN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FTN-RATED-PREMIUM             PIC 9(9)V9(2).

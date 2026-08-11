******************************************************************
*  COPYBOOK  : GFNMR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : NM
******************************************************************
 01  RT-FNM-RATING.

          03 RT-FNM-TERRITORY-CODE            PIC X(3).
          03 RT-FNM-CLASS-CODE                PIC X(4).
          03 RT-FNM-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FNM-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FNM-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FNM-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FNM-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FNM-RATED-PREMIUM             PIC 9(9)V9(2).

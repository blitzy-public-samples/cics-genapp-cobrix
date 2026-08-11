******************************************************************
*  COPYBOOK  : GFVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : VA
******************************************************************
 01  RT-FVA-RATING.

          03 RT-FVA-TERRITORY-CODE            PIC X(3).
          03 RT-FVA-CLASS-CODE                PIC X(4).
          03 RT-FVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FVA-RATED-PREMIUM             PIC 9(9)V9(2).

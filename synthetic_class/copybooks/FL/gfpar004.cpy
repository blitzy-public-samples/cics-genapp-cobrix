******************************************************************
*  COPYBOOK  : GFPAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : PA
******************************************************************
 01  RT-FPA-RATING.

          03 RT-FPA-TERRITORY-CODE            PIC X(3).
          03 RT-FPA-CLASS-CODE                PIC X(4).
          03 RT-FPA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FPA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FPA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FPA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FPA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FPA-RATED-PREMIUM             PIC 9(9)V9(2).
